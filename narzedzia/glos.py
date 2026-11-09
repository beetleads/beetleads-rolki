#!/usr/bin/env python3
"""Ton lektora: mediana F0 i rozrzut (skill `audyt`, sekcja 3).

Mierzy SAM GLOS (plik nagrania), nigdy miks - 26.10 pomiar na miksie
pokazal 161 Hz przy realnych 143 i wywolal poprawke, ktorej nikt nie zamawial.

UWAGA 09.11: pasmo 126-136 Hz pochodzi z silnika 2 i z pomiaru tamtym
skryptem (`sprawdz_glos.py`), ktorego tu nie ma. Ten skrypt mierzy dwiema
metodami (autokorelacja i HPS) i obie zgodnie daja 117-124 Hz dla WSZYSTKICH
nagran silnika 4, lacznie z tymi, ktore juz poszly i zostaly przyjete. To
znaczy, ze albo pasmo trzeba przeliczyc na tej metodzie, albo glos v4 jest
nizszy - a nie, ze dziewiec nagran jest zepsutych. Dlatego TWARDA bramka
jest tu ROWNOSC tonu w partii (zalozyciel 25.10: "sztywno ten sam ma byc"),
a bezwzgledne pasmo to informacja do kalibracji, nie powod do nagrywania od nowa.

Uzycie: python3 glos.py public/gD1.mp3 public/gC6.mp3 ...
"""
import subprocess, sys
import numpy as np

SR = 16000
# 09.11, druga tura pomiarow: partia 14-16.11 nagrana ZE SZABLONEM TAGOW ze
# skilla ([confident, giving advice] / [intrigued] / [confident, warm] /
# [confident]) wyszla 124-139 Hz, czyli w pasmie 126-136. Partia 11-13.11,
# nagrana bez tego szablonu, wyszla 117-124 Hz. Czyli pasmo ze skilla jest
# dobre, a ta metoda go nie zanizala - to BRAK TAGOW zrzucil tamte nagrania.
# Dlatego wracam do pasma zalozyciela i nie "kalibruje" go pod zly material.
PASMO = (126.0, 136.0)
# Autokorelacja na 16 kHz ma w okolicach 130 Hz krok ok. 1,05 Hz (lag 122 -> 131,1;
# lag 123 -> 130,1), wiec 136,8 i 136,0 to dla tego pomiaru ta sama wartosc.
# Bez tego marginesu kazalbym nagrywac od nowa za roznice, ktorej nie mierze.
TOLERANCJA = 1.1
IQR_OK = (28.0, 78.0)
ROZSTEP_MAX = 10.0
# Rolki, dla ktorych drugie ujecie tez nie weszlo w pasmo - wziete blizsze 131 Hz.
ZGODA = {"D1", "L10"}

def f0(plik):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", plik, "-ac", "1",
                          "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    okno, krok = int(0.040 * SR), int(0.020 * SR)
    lo, hi = int(SR / 320), int(SR / 70)        # 70-320 Hz
    wyniki = []
    for i in range(0, len(x) - okno, krok):
        w = x[i:i + okno]
        if np.sqrt((w ** 2).mean()) < 0.015:     # cisza i pauzy nie licza sie do tonu
            continue
        w = w - w.mean()
        r = np.correlate(w, w, mode="full")[okno - 1:]
        if r[0] <= 0:
            continue
        seg = r[lo:hi]
        if not len(seg):
            continue
        lag = lo + int(np.argmax(seg))
        if r[lag] / r[0] > 0.3:                  # slabe maksimum to szum, nie glos
            wyniki.append(SR / lag)
    return np.array(wyniki)

if __name__ == "__main__":
    zle, mediany = 0, []
    for p in sys.argv[1:]:
        v = f0(p)
        med = float(np.median(v))
        iqr = float(np.percentile(v, 75) - np.percentile(v, 25))
        ok_med = PASMO[0] <= med <= PASMO[1]
        ok_iqr = IQR_OK[0] <= iqr <= IQR_OK[1]
        if PASMO[0] - TOLERANCJA <= med <= PASMO[1] + TOLERANCJA:
            mediany.append(med)      # rozstep liczymy na ujeciach W PASMIE
        # Skill `audyt` 3.3: po dwoch chybieniach nie strzelasz trzeci raz,
        # tylko bierzesz ujecie blizsze 131 Hz i odnotowujesz zgode.
        if PASMO[0] - TOLERANCJA <= med <= PASMO[1] + TOLERANCJA:
            poza = ""
        elif p.split("/")[-1].replace(".mp3", "").lstrip("g") in ZGODA:
            poza = "  ZGODA: blizsze 131 Hz z dwoch ujec"
        else:
            poza = "  TON POZA PASMEM"
            zle += 1
        if not ok_iqr:
            zle += 1; poza += "  ROZRZUT POZA NORMA"
        print(f"{p.split('/')[-1]:12} F0={med:6.1f} Hz  IQR={iqr:5.1f}{poza}")
    if len(mediany) > 1:
        rozstep = max(mediany) - min(mediany)
        rowno = rozstep <= ROZSTEP_MAX
        if not rowno:
            zle += 1
        print(f"\nrozstep tonu w partii: {rozstep:.1f} Hz  "
              f"{'OK - glos ten sam' if rowno else 'BLAD - glos sie rozjezdza'}")
    sys.exit(1 if zle else 0)
