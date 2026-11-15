#!/usr/bin/env python3
"""Remiks zaplanowanej rolki: muzyka +3 dB (12 -> 9 dB pod lektorem) i wyciete wdechy.

Nie rusza obrazu ani glosu: do oryginalnego miksu DODAJE wyseparowany podklad
(fazowo zgodny), a w okienkach wdechu ODEJMUJE wyseparowany glos.
Uzycie: python3 remiks.py wejscie.mp4 wyjscie.mp4 [katalog_stemow]
"""
import json, subprocess, sys, os
import numpy as np
from scipy.io import wavfile
from scipy import signal as sg

SR = 44100
POD_GLOSEM = 9.0            # cel: muzyka tyle dB pod lektorem (skill rolki-v6, 15.11)
MAX_PODBICIE_DB = float(os.environ.get("REMIKS_MAX", 14.0))   # bezpiecznik, zeby bit nie wszedl na lektora
FADE_MS = 15


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def bas_tab(y, sr=SR):
    """to samo co bas(), ale z tablicy: fragment 2-10 s, mono, 8 kHz"""
    m = y.mean(1)[int(2 * sr):int(10 * sr)]
    if len(m) < 1000:
        m = y.mean(1)
    m = sg.resample_poly(m, 8000, sr)
    X = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1 / 8000)
    return float(100 * X[(f >= 20) & (f <= 120)].sum() / X.sum())


def bas(p):
    """udzial 20-120 Hz jak narzedzia/bas.py - miara, czy muzyke slychac"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "2", "-t", "8", "-i", p,
                          "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    X = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / 8000)
    return float(100 * X[(f >= 20) & (f <= 120)].sum() / X.sum())


def lufs(p):
    e = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-i", p, "-af",
                        "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float([l for l in e.splitlines() if l.strip().startswith("I:")][-1].split()[1])


def wczytaj(p):
    sr, x = wavfile.read(p)
    x = x.astype(np.float32) / 32768.0 if x.dtype == np.int16 else x.astype(np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    assert sr == SR, f"{p}: {sr}"
    return x


def slowa(p):
    import json as _j
    cache = p + ".slowa.json"
    if os.path.exists(cache):
        return [tuple(w) for w in _j.load(open(cache))]
    """Slowa lektora z czasami - maska mowy, ktorej nie wolno tknac."""
    from faster_whisper import WhisperModel
    global _M
    try:
        _M
    except NameError:
        _M = WhisperModel("small", device="cpu", compute_type="int8")
    import numpy as _np
    from scipy.io import wavfile as _wf
    t = "/tmp/_mowa.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ac", "1", "-ar", "16000", t], check=True)
    _, x = _wf.read(t)
    segs, _i = _M.transcribe((x.astype(_np.float32) / 32768.0), language="pl",
                             beam_size=5, word_timestamps=True)
    out = []
    for sg in segs:
        for w in (sg.words or []):
            out.append((w.start, w.end, w.word.strip()))
    _j.dump(out, open(cache, "w"))
    return out


def wdechy(v, sr=SR):
    """Okna wdechu/oddechu w sladzie glosu: szum bez tonu, miedzy zdaniami."""
    m = v.mean(1)
    okno, skok = int(0.025 * sr), int(0.010 * sr)
    f, t, S = sg.stft(m, sr, nperseg=okno, noverlap=okno - skok)
    mag = np.abs(S) + 1e-10
    en = 20 * np.log10(mag.sum(0))
    szczyt = np.percentile(en, 97)
    nisk = mag[(f >= 60) & (f < 300)].sum(0)
    sred = mag[(f >= 500) & (f < 4000)].sum(0)
    calosc = mag.sum(0)
    plaskosc = np.exp(np.log(mag[(f > 200) & (f < 8000)]).mean(0)) / mag[(f > 200) & (f < 8000)].mean(0)
    # wdech: cicho wzgledem mowy, ale slyszalnie; energia w srednich, malo w niskich; szumowy
    kand = (en < szczyt - 11) & (en > szczyt - 42) & (nisk / calosc < 0.34) & (sred / calosc > 0.33) & (plaskosc > 0.11)
    # zabezpieczenie: jesli w ramce jest ton krtaniowy (mowa), to nie wdech
    for i in np.flatnonzero(kand):
        a = int(t[i] * sr)
        seg = m[max(0, a - okno // 2): a + okno]
        if len(seg) < okno:
            continue
        seg = seg - seg.mean()
        if np.abs(seg).max() < 1e-5:
            continue
        ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
        ac /= ac[0] + 1e-12
        lo, hi = int(sr / 300), int(sr / 80)
        if len(ac) > hi and ac[lo:hi].max() > 0.45:
            kand[i] = False
    # scal w odcinki 0,06-0,60 s
    odc, start = [], None
    for i, k in enumerate(np.r_[kand, False]):
        if k and start is None:
            start = i
        elif not k and start is not None:
            a, b = t[start], t[min(i, len(t) - 1)]
            if 0.06 <= b - a <= 0.60:
                odc.append((float(a), float(b)))
            start = None
    return odc


def maska(n, odc, sr=SR):
    m = np.zeros(n, np.float32)
    f = int(FADE_MS / 1000 * sr)
    for a, b in odc:
        i, j = int(a * sr), int(b * sr)
        i, j = max(0, i - f), min(n, j + f)
        if j - i < 3 * f:
            continue
        seg = np.ones(j - i, np.float32)
        seg[:f] = np.linspace(0, 1, f)
        seg[-f:] = np.linspace(1, 0, f)
        m[i:j] = np.maximum(m[i:j], seg)
    return m


def main(wej, wyj, kat="/home/claude/mc/sep"):
    baza = os.path.splitext(os.path.basename(wej))[0]
    rob = os.path.join(kat, baza)
    os.makedirs(rob, exist_ok=True)
    mix_wav = os.path.join(rob, "mix.wav")
    sh(["ffmpeg", "-v", "error", "-y", "-i", wej, "-vn", "-ac", "2", "-ar", str(SR), mix_wav])
    if not os.path.exists(os.path.join(rob, "htdemucs", "mix", "vocals.wav")):
        sh(["python3", "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs", "-o", rob, mix_wav])
    v = wczytaj(os.path.join(rob, "htdemucs", "mix", "vocals.wav"))
    nv = wczytaj(os.path.join(rob, "htdemucs", "mix", "no_vocals.wav"))
    mix = wczytaj(mix_wav)
    n = min(len(v), len(nv), len(mix))
    v, nv, mix = v[:n], nv[:n], mix[:n]
    odc = wdechy(v)
    # twardy filtr: nie tykamy niczego, co lezy na slowie lektora (margines 40 ms)
    sl = slowa(os.path.join(rob, "htdemucs", "mix", "vocals.wav"))
    MARG = 0.05
    # kazde okno przycinamy do luki miedzy slowami; co nie zmiesci sie - odpada
    przyciete = []
    for a, b in odc:
        for ws, we, _ in sl:
            if a < we + MARG and b > ws - MARG:      # nachodzi na slowo
                if a < ws:                            # koniec okna wchodzi w slowo
                    b = min(b, ws - MARG)
                else:                                 # start okna siedzi w slowie
                    a = max(a, we + MARG)
        if b - a >= 0.05:
            przyciete.append((a, b))
    odc = przyciete
    m = maska(n, odc)[:, None]
    # muzyka: ile dB brakuje, zeby byla POD_GLOSEM pod lektorem
    l_v = lufs(os.path.join(rob, "htdemucs", "mix", "vocals.wav"))
    l_nv = lufs(os.path.join(rob, "htdemucs", "mix", "no_vocals.wav"))
    podbicie = min(max((l_v - POD_GLOSEM) - l_nv, 0.0), MAX_PODBICIE_DB)
    # rolka bez podkladu: nie ma czego podglasniac - dokladamy firmowy bit
    BIT = "/home/claude/rolki/silnik6/podklad_bit.mp3"
    brak_muzyki = (l_v - l_nv) > 30
    if brak_muzyki and os.path.exists(BIT):
        bit_wav = os.path.join(rob, "bit.wav")
        d = n / SR
        sh(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", BIT, "-t", f"{d:.3f}",
            "-af", f"afade=t=in:d=0.5,afade=t=out:st={max(d - 1.2, 0):.2f}:d=1.2",
            "-ac", "2", "-ar", str(SR), bit_wav])
        bit = wczytaj(bit_wav)[:n]
        if len(bit) < n:
            bit = np.pad(bit, ((0, n - len(bit)), (0, 0)))
        l_bit = lufs(bit_wav)
        nv = bit * 10 ** (((l_v - POD_GLOSEM) - l_bit) / 20)   # bit na poziomie celu
        podbicie = 0.0
    k = 10 ** (podbicie / 20)
    out_wav = os.path.join(rob, "nowy.wav")

    def miks_tab(podb):
        kk = 10 ** (podb / 20)
        y = mix + (kk if brak_muzyki else kk - 1) * nv - m * v
        sz = np.abs(y).max()
        if sz > 0.98:
            y *= 0.98 / sz
        return y

    def zapisz(y):
        wavfile.write(out_wav, SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
        sh(["ffmpeg", "-v", "error", "-y", "-i", wej, "-i", out_wav, "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.6:LRA=11,alimiter=limit=0.8:level=disabled",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", wyj])

    def zrob(podb):
        return bas_tab(miks_tab(podb))

    # kalibracja: muzyke ma byc slychac (bas 10-13%), ale lektor zostaje na wierzchu
    proby = []
    b = zrob(podbicie)
    proby.append((round(podbicie, 1), round(b, 1)))
    for _ in range(4):
        if 10.0 <= b <= 13.0:
            break
        if b < 10.0 and podbicie >= MAX_PODBICIE_DB:
            break          # glosniej nie wolno - lektor ma byc na wierzchu
        if b > 13.0 and podbicie <= (-24.0 if brak_muzyki else 0.0):
            break
        krok = -2.0 if b > 13.0 else 1.5
        podbicie = min(max(podbicie + krok, -24.0 if brak_muzyki else 0.0), MAX_PODBICIE_DB)
        b = zrob(podbicie)
        proby.append((round(podbicie, 1), round(b, 1)))
    zapisz(miks_tab(podbicie))
    b = bas(wyj)        # kontrola na gotowym pliku, po loudnorm
    print(json.dumps({"plik": os.path.basename(wyj), "wdechy": len(odc),
                      "lektor_LUFS": round(l_v, 1), "muzyka_LUFS": round(l_nv, 1),
                      "muzyka_bylo_dB_pod": round(l_v - l_nv, 1), "dolozony_bit": bool(brak_muzyki),
                      "podbicie_dB": round(podbicie, 1), "slow_lektora": len(sl), "bas_proc": round(b, 1), "kalibracja": proby,
                      "sek_wdechow": round(sum(b - a for a, b in odc), 2),
                      "odcinki": [[round(a, 2), round(b, 2)] for a, b in odc]}, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:])
