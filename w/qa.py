#!/usr/bin/env python3
"""qa.py <katalog_rolki> - kontrola gotowej rolki (final.mp4):
długość <= 20,05 s, strumień audio, LUFS ok. -15, true peak <= -1,5, f0 głosu 126-136 Hz,
transkrypcja final.mp4 vs tekst scenariusza (brakujące słowa = ucięty głos), CTA raz, arkusz klatek co 0,5 s."""
import sys, os, json, re, subprocess, difflib
import numpy as np, soundfile as sf

d = os.path.abspath(sys.argv[1]); f = f'{d}/final.mp4'
spec = json.load(open(f'{d}/spec.json'))
def run(*a): return subprocess.run(a, capture_output=True, text=True)
pr = json.loads(run('ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'json', f).stdout)
dur = float(pr['format']['duration']); has_a = any(s['codec_type'] == 'audio' for s in pr['streams'])
eb = run('ffmpeg', '-hide_banner', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-').stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', eb)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', eb)[-1])
# f0 głosu (pyin)
import librosa
y, sr = librosa.load(f'{d}/voice_t.wav', sr=16000)
f0a, vf, _ = librosa.pyin(y, fmin=70, fmax=300, sr=sr); f0 = float(np.nanmedian(f0a[vf]))
# transkrypcja gotowego pliku
from faster_whisper import WhisperModel
import scipy.signal as sg
run('ffmpeg', '-v', 'error', '-y', '-i', f, '-ac', '1', '-ar', '16000', '/tmp/_q.wav')
a, _ = sf.read('/tmp/_q.wav')
m = WhisperModel('small', device='cpu', compute_type='int8')
seg, _ = m.transcribe(a.astype(np.float32), language='pl')
txt = ' '.join(s.text for s in seg)
norm = lambda t: [re.sub(r'[^0-9a-ząćęłńóśźż]', '', w.lower()) for w in t.split() if re.sub(r'[^0-9a-ząćęłńóśźż]', '', w.lower())]
ref = norm(spec['text']); hyp = norm(txt)
sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False); ratio = sm.ratio()
miss = [ref[i] for op, i1, i2, j1, j2 in sm.get_opcodes() if op in ('delete',) for i in range(i1, i2)]
cta_n = len(re.findall(r'zaobserwuj', txt.lower()))
# arkusz klatek co 0,5 s
run('ffmpeg', '-v', 'error', '-y', '-i', f, '-vf', 'fps=2,scale=216:-1,tile=8x5', '-frames:v', '1', f'{d}/sheet.jpg')
ok = 126 <= f0 <= 136 and dur <= 20.05 and has_a and -16.5 <= I <= -13.5 and TP <= -1.0 and cta_n == 1 and ratio > 0.8
res = {'ok': ok, 'dlugosc': round(dur, 2), 'audio': has_a, 'LUFS': I, 'TP': TP, 'f0': round(f0, 1), 'zgodnosc_tekstu': round(ratio, 2),
       'brakuje_slow': miss, 'CTA_razy': cta_n, 'transkrypcja': txt.strip()}
json.dump(res, open(f'{d}/qa.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False))
