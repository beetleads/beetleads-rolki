#!/usr/bin/env python3
"""Przygotowanie dzwieku rolki (10.11, uwagi zalozyciela):
  - glos nizej o 4% (asetrate + atempo, tempo bez zmian)
  - BEZ efektow dzwiekowych przy zmianie ujecia: stare miksy z AI Producera maja
    wpalone whooshe na cieciach; tlumimy transjenty wysokopasmowe, ale TYLKO tam,
    gdzie nie ma mowy (brak energii w 150-400 Hz), zeby nie ruszyc lektora.
"""
import subprocess, sys, numpy as np, wave

SR = 48000

def wczytaj(p):
    raw = subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def pasmo(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))

def zapisz(x, p):
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()); w.close()

def przygotuj(wej, wyj, pitch=0.90):
    """pitch 0,90 = glos nizszy o 10%.

    10.11: pierwsza wersja robila to przez asetrate + atempo i SKRACALA nagranie
    o 1,4 s - napisy rozjezdzaly sie z glosem narastajaco przez cala rolke.
    `rubberband` przestraja bez ruszania dlugosci; i tak sprawdzamy ja ponizej.
    """
    tmp = wyj + ".pitch.wav"
    subprocess.run(["ffmpeg","-y","-v","error","-i",wej,"-af",f"rubberband=pitch={pitch}",
                    "-ac","1","-ar",str(SR),tmp], check=True)
    def dlugosc(p):
        return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                     "-of","csv=p=0",p], capture_output=True, text=True).stdout)
    assert abs(dlugosc(tmp) - dlugosc(wej)) < 0.05, "pitch zmienil dlugosc - napisy sie rozjada"
    x = wczytaj(tmp)
    okno = int(0.02 * SR)
    n = len(x) // okno
    wys = np.array([np.sqrt((pasmo(x[i*okno:(i+1)*okno], 3500, 9000)**2).mean()) for i in range(n)])
    mowa = np.array([np.sqrt((pasmo(x[i*okno:(i+1)*okno], 150, 400)**2).mean()) for i in range(n)])
    # Kryterium musi byc WASKIE: pierwsza wersja (percentyl 75 x 2,6) zbila mowe
    # o 3,7 dB i muzyke o 4,6 dB - czyli tlumila cala rolke, nie whooshe.
    prog_w = np.percentile(wys, 92) * 1.8
    prog_m = np.percentile(mowa, 35)
    wzm = np.ones(n)
    trafione = 0
    for i in range(1, n):
        skok = 20 * np.log10((wys[i] + 1e-9) / (wys[i-1] + 1e-9))
        if wys[i] > prog_w and mowa[i] < prog_m and skok > 10:
            wzm[i:i+3] = 0.55                # ok. -5 dB na 60 ms
            trafione += 1
    krzywa = np.interp(np.arange(len(x)), np.arange(n) * okno + okno / 2, wzm)
    krzywa = np.convolve(krzywa, np.ones(int(0.01*SR))/int(0.01*SR), mode="same")
    zapisz(x * krzywa, wyj)
    print(wyj, "| stlumione transjenty:", trafione)

if __name__ == "__main__":
    for p in sys.argv[1:]:
        przygotuj(p, p.replace("audio_", "glos_"))
