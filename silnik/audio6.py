#!/usr/bin/env python3
"""Przygotowanie dzwieku rolki - wersja 6 (10.11 20:49: "glos ma byc normalny").

Co poszlo zle w wersji 5 i czego tu NIE robimy:
  - `rubberband` (nawet przy pitch=1.0) przepuszczal caly material przez wokoder
    fazowy - glos robil sie metaliczny;
  - mix byl skladany do MONO, a lektor i muzyka sa w stereo - zlozenie faz wyjadalo
    srodek pasma, czyli dokladnie glos;
  - tlumienie whooszy dzialalo SZEROKOPASMOWO, wiec przyciszalo tez lektora.

Wersja 6: material zostaje stereo, w oryginalnym tonie i tempie. Whooshe z cieciami
(zalozyciel: "przy zmianach slajdu nie dawaj efektu dzwiekowego") tlumimy WYLACZNIE
w pasmie 3,5-9 kHz, rozdzielajac sygnal na pasma i skladajac z powrotem - dzieki temu
pasmo mowy (150-3500 Hz) zostaje nietkniete, co skrypt sprawdza na koncu.
"""
import subprocess, sys, numpy as np, wave

SR = 48000
LO, HI = 3500, 9000


def wczytaj(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "2", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    return x.reshape(-1, 2)


def filtr(x, lo, hi):
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    maska = (f >= lo) & (f <= hi)
    Y = np.zeros_like(X)
    Y[maska] = X[maska]
    return np.fft.irfft(Y, x.shape[0], axis=0)


def rms(x):
    return float(np.sqrt((x ** 2).mean()) + 1e-12)


def zapisz(x, p):
    w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()); w.close()


def przygotuj(wej, wyj):
    x = wczytaj(wej)
    gora = filtr(x, LO, HI)
    reszta = x - gora
    mowa = filtr(x, 150, 400)
    okno = int(0.02 * SR)
    n = x.shape[0] // okno
    w_g = np.array([rms(gora[i*okno:(i+1)*okno]) for i in range(n)])
    w_m = np.array([rms(mowa[i*okno:(i+1)*okno]) for i in range(n)])
    prog_g, prog_m = np.percentile(w_g, 92) * 1.8, np.percentile(w_m, 35)
    wzm = np.ones(n)
    traf = 0
    for i in range(1, n):
        skok = 20 * np.log10(w_g[i] / w_g[i-1]) if w_g[i-1] > 0 else 0
        if w_g[i] > prog_g and w_m[i] < prog_m and skok > 10:
            wzm[i:i+3] = 0.4                  # -8 dB, ale TYLKO w pasmie 3,5-9 kHz
            traf += 1
    krzywa = np.interp(np.arange(x.shape[0]), np.arange(n) * okno + okno / 2, wzm)
    k = int(0.01 * SR)
    krzywa = np.convolve(krzywa, np.ones(k) / k, mode="same")[:, None]
    y = reszta + gora * krzywa
    zapisz(y, wyj)
    # kontrola: pasmo mowy nie moze sie ruszyc
    d = 20 * np.log10(rms(filtr(y, 150, 3500)) / rms(filtr(x, 150, 3500)))
    print(f"{wyj} | transjenty: {traf} | pasmo mowy: {d:+.2f} dB")
    assert abs(d) < 0.3, "obrobka ruszyla pasmo mowy"


if __name__ == "__main__":
    przygotuj(sys.argv[1], sys.argv[2])
