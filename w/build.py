#!/usr/bin/env python3
"""build.py <katalog_rolki>
Wejście w katalogu: spec.json, voice.mp3 (ElevenLabs, głos ROLKI), bg*.jpg (opcjonalnie).
Wyjście: words.json, mix.wav, data.js (+ kopie gen.html/icons.js/logo.png) gotowe do render.py.
"""
import json, os, re, subprocess, sys, shutil
import numpy as np, soundfile as sf, scipy.signal as sg

W = os.path.dirname(os.path.abspath(__file__))
SR = 48000
ATEMPO = 1.12

def sh(*a): subprocess.run(a, check=True)

def load(p):
    tmp = '/tmp/_l.wav'
    sh('ffmpeg', '-v', 'error', '-y', '-i', p, '-ac', '1', '-ar', str(SR), tmp)
    a, _ = sf.read(tmp); return a.astype(np.float32)

def norm(w): return re.sub(r'[^0-9a-ząćęłńóśźż%]', '', w.lower())

def words_of(pcm48):
    from faster_whisper import WhisperModel
    pcm = sg.resample_poly(pcm48, 1, 3).astype(np.float32)
    m = WhisperModel('small', device='cpu', compute_type='int8')
    seg, _ = m.transcribe(pcm, language='pl', word_timestamps=True, vad_filter=False)
    out = []
    for s in seg:
        for w in s.words: out.append({'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)})
    return out

def phrases(words, kw, hook_until):
    """frazy 2-4 słowa, łamane na interpunkcji, bez samotnych krótkich słów"""
    ph, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        end_punct = bool(re.search(r'[.,:;?!\-]$', w['w']))
        nxt = words[i + 1] if i + 1 < len(words) else None
        n = len(cur)
        sent_end = bool(re.search(r'[.?!]$', w['w']))
        brk = sent_end or (end_punct and n >= 2) or n >= 4 or nxt is None
        if brk and nxt is not None and n == 4 and len(norm(nxt['w'])) <= 2 and not end_punct:
            brk = False  # nie zostawiaj "z", "do" na początek następnej frazy
        if n >= 5: brk = True
        if brk:
            ph.append(cur); cur = []
    # krótkie słowo funkcyjne (i, do, w, z...) nie kończy frazy - przechodzi do następnej
    for k in range(len(ph) - 1):
        while len(ph[k]) > 2 and len(norm(ph[k][-1]['w'])) <= 2 and not re.search(r'[.,:;?!”"]$', ph[k][-1]['w']):
            ph[k + 1].insert(0, ph[k].pop())
    # dołącz pojedyncze słowa do poprzedniej frazy
    fixed = []
    for p in ph:
        if len(p) == 1 and fixed and len(fixed[-1]) < 5: fixed[-1] += p
        else: fixed.append(p)
    caps = []
    for p in fixed:
        html = []
        for w in p:
            t = w['w']
            isk = any(k in norm(t) for k in kw) or bool(re.search(r'\d', t))
            html.append(f'<span class="w{" k" if isk else ""}">{t}</span>')
        caps.append({'s': p[0]['s'], 'e': p[-1]['e'], 'html': ' '.join(html), 'hook': bool(p[0]['s'] < hook_until)})
    for i, c in enumerate(caps):  # widoczna do następnej frazy, min 0,8 s
        nxt = caps[i + 1]['s'] if i + 1 < len(caps) else c['e'] + 0.6
        c['e'] = max(nxt, c['s'] + 0.8) if i + 1 < len(caps) else max(c['e'] + 0.5, c['s'] + 0.8)
        if i + 1 < len(caps) and c['e'] > caps[i + 1]['s']: caps[i + 1]['s'] = c['e']
    return caps

def align(text, wwords):
    """słowa ze scenariusza (poprawna pisownia) z czasami z whispera; brakujące - interpolacja"""
    import difflib
    toks = text.split()
    a = [norm(t) for t in toks]; b = [norm(w['w']) for w in wwords]
    tm = [None] * len(toks)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size): tm[blk.a + k] = (wwords[blk.b + k]['s'], wwords[blk.b + k]['e'])
    # liczby: "34%" vs "34","%" - dopasuj po kolejności czasu
    T0 = wwords[0]['s'] if wwords else 0; T1 = wwords[-1]['e'] if wwords else 1
    known = [i for i, x in enumerate(tm) if x]
    for i in range(len(toks)):
        if tm[i]: continue
        lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
        ts = tm[lo][1] if lo is not None else T0; te = tm[hi][0] if hi is not None else T1
        n = (hi if hi is not None else len(toks)) - (lo if lo is not None else -1)
        pos = i - (lo if lo is not None else -1)
        st = ts + (te - ts) * (pos - 1) / max(1, n - 1); tm[i] = (st, st + (te - ts) / max(1, n - 1))
    return [{'w': t, 's': round(x[0], 3), 'e': round(x[1], 3)} for t, x in zip(toks, tm)]

def find_anchor(words, anchor, after=0):
    a = [norm(x) for x in anchor.split()]
    toks = [norm(w['w']) for w in words]
    for i in range(after, len(toks)):
        if toks[i:i + len(a)] == a: return i
    for i in range(after, len(toks)):  # luźniej: pierwsze słowo
        if toks[i] == a[0]: return i
    raise SystemExit(f'Nie znaleziono kotwicy sceny: {anchor}')

def main(d):
    spec = json.load(open(f'{d}/spec.json'))
    # 1) głos: obcięcie ciszy na brzegach + atempo 1.10 (bez zmiany wysokości)
    sh('ffmpeg', '-v', 'error', '-y', '-i', f'{d}/voice.mp3', '-af',
       f'silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,atempo={ATEMPO}',
       '-ac', '1', '-ar', str(SR), f'{d}/voice_t.wav')
    v, _ = sf.read(f'{d}/voice_t.wav'); v = v.astype(np.float32)
    lead = 0.12; v = np.concatenate([np.zeros(int(lead * SR), np.float32), v])
    words = align(spec['text'], words_of(v))
    json.dump(words, open(f'{d}/words.json', 'w'), ensure_ascii=False, indent=0)
    V = len(v) / SR
    # 2) sceny wg kotwic (zmiana tylko między słowami)
    scenes = spec['scenes']; idx = 0
    for k, sc in enumerate(scenes):
        if k == 0: sc['s'] = 0.0; continue
        i = find_anchor(words, sc['at'], idx); idx = i
        prev_end = words[i - 1]['e'] if i > 0 else 0
        sc['s'] = round(max(prev_end + 0.02, words[i]['s'] - 0.12), 3)
    cta_s = round(V + 0.25, 3)
    end = cta_s + 2.64 + 0.55
    caps = phrases(words, [norm(k) for k in spec.get('kw', [])], hook_until=scenes[1]['s'] if len(scenes) > 1 else 2)
    bgs = spec.get('bgs', [])
    data = {'scenes': scenes, 'caps': caps, 'ctaS': cta_s, 'end': round(end, 3), 'bgs': bgs, 'seed': spec.get('seed', 0)}
    open(f'{d}/data.js', 'w').write('window.DATA=' + json.dumps(data, ensure_ascii=False) + ';')
    for f in ['gen.html', 'icons.js', 'logo.png']: shutil.copy(f'{W}/{f}', d)
    # 3) miks: głos + CTA + efekty + bit2 cicho
    N = int(end * SR); mix = np.zeros(N, np.float32)
    mix[:len(v)] += v
    cta = load(f'{W}/cta_porad.wav'); c0 = int(cta_s * SR); mix[c0:c0 + len(cta)] += cta[:N - c0]
    vo = mix.copy()
    def sfx(name, t, peak_db=-21):
        a = load(f'{W}/sfx/{name}.wav'); a = a[:int(1.5 * SR)]
        f = int(0.15 * SR); a[-f:] *= np.linspace(1, 0, f)
        a *= 10 ** (peak_db / 20) / (np.abs(a).max() + 1e-9)
        s0 = int(t * SR); mix[s0:s0 + len(a)] += a[:max(0, N - s0)]
    sfx('whoosh', 0.0, -24)
    for k, sc in enumerate(scenes):
        if k > 0: sfx('whoosh', max(0, sc['s'] - 0.05), -24)
        ty = sc['type']
        if ty == 'num' and k > 0: sfx('bell', sc['s'] + 0.45, -19)
        elif ty == 'num': sfx('sparkle', 0.05, -23)
        elif ty == 'check':
            for j, _ in enumerate(sc['items']): sfx('marimba', sc['s'] + 0.4 + j * 0.55, -22)
        elif ty in ('card',): sfx('paper', sc['s'] + 0.2, -21); sfx('sparkle', sc['s'] + 0.55, -24)
        elif ty in ('vs', 'icons'): sfx('tap', sc['s'] + 0.3, -22); sfx('marimba', sc['s'] + 0.8, -23)
        elif ty in ('bars', 'donut'): sfx('marimba', sc['s'] + 0.9, -22)
        elif ty == 'icon': sfx('tap', sc['s'] + 0.25, -22)
    sfx('whoosh', cta_s - 0.05, -24); sfx('tap', cta_s + 1.2, -20)
    # bit: ok. 14 dB pod głosem
    beat = load(f'{W}/beat2.mp3')
    reps = int(np.ceil(N / len(beat))) + 1; beat = np.tile(beat, reps)[:N]
    def rms(x): return np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2)) + 1e-9
    beat *= (rms(vo[:len(v)]) / rms(beat)) * 10 ** (-14 / 20)
    fi, fo = int(0.3 * SR), int(1.4 * SR)
    beat[:fi] *= np.linspace(0, 1, fi); beat[-fo:] *= np.linspace(1, 0, fo)
    mix += beat
    # głośność: -15 LUFS, szczyt <= -2 dBFS
    import pyloudnorm as pyln
    meter = pyln.Meter(SR); L = meter.integrated_loudness(mix)
    mix *= 10 ** ((-18 - L) / 20)  # mono -18 = stereo -15 LUFS
    pk = np.abs(mix).max()
    if pk > 10 ** (-2 / 20):  # miękki limiter: kompresja tylko szczytów
        thr = 10 ** (-3 / 20)
        a = np.abs(mix); over = a > thr
        mix[over] = np.sign(mix[over]) * (thr + (a[over] - thr) * 0.25)
        mix *= min(1, 10 ** (-2 / 20) / np.abs(mix).max())
    sf.write(f'{d}/mix.wav', np.stack([mix, mix], 1), SR, subtype='PCM_16')
    print(json.dumps({'dlugosc': round(end, 2), 'glos': round(V, 2), 'cta': cta_s, 'LUFS_przed': round(L, 1), 'scen': len(scenes), 'fraz': len(caps)}))

if __name__ == '__main__':
    main(sys.argv[1])
