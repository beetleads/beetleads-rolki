"""Bramka startu: pierwsza sekunda rolki musi sie ruszac.
Stara koncowka (bez efektu na starcie) ma ruch ~1-4, silnik 5 z efektem ~19-34.
Uzycie: python3 sprawdz_start.py plik.mp4 [...]"""
import subprocess, sys
import numpy as np
PROG = 10.0

def klatka(plik, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", plik,
                          "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).astype(float)

def ruch(plik):
    a, b, c = klatka(plik, 0.25), klatka(plik, 0.45), klatka(plik, 0.75)
    return abs(a - b).mean(), abs(b - c).mean()

if __name__ == "__main__":
    zle = 0
    for p in sys.argv[1:]:
        r1, r2 = ruch(p)
        ok = max(r1, r2) >= PROG
        print(f"{p}\truch {r1:.1f}/{r2:.1f}\t{'OK' if ok else 'BRAK EFEKTU NA STARCIE'}")
        zle += not ok
    sys.exit(1 if zle else 0)
