#!/usr/bin/env python3
"""Podklad muzyczny pod gotowa rolke silnika 6 (12.11 16:15: "podloz muzyke").

Muzyka zapetlona do dlugosci filmu, wejscie 0,5 s, zejscie 1,2 s przed koncem,
przyciszana pod lektorem (sidechain), calosc -14 LUFS, szczyt <= -1,5 dBTP.
Glosnosc podkladu dobierana tak, zeby udzial pasma 20-120 Hz wyszedl 9-15%
(dowod, ze muzyka jest, a nie zaglusza glosu - jak w produkuj.sh starych rolek).
Obraz kopiowany bez ponownego kodowania.

Uzycie: python3 podklad.py gotowa.mp4 muzyka.mp3 wyjscie.mp4
"""
import subprocess, sys, json

BAS = "/home/claude/beetleads-rolki/narzedzia/bas.py"


def dl(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p],
                       capture_output=True, text=True).stdout
    return float(json.loads(o)["format"]["duration"])


def miks(wej, muz, wyj, g):
    d = dl(wej)
    fc = (f"[1:a]atrim=0:{d:.2f},asetpts=PTS-STARTPTS,afade=t=in:d=0.5,"
          f"afade=t=out:st={d - 1.2:.2f}:d=1.2,volume={g}[m];"
          "[0:a]asplit[v][sc];"
          "[m][sc]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=350[md];"
          "[v][md]amix=inputs=2:duration=first:normalize=0,"
          f"loudnorm=I=-14:TP=-1.6:LRA=11,alimiter=limit=0.8:level=disabled,afade=t=out:st={d - 0.7:.2f}:d=0.7[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wej, "-stream_loop", "-1", "-i", muz,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", wyj], check=True)
    return float(subprocess.run(["python3", BAS, wyj], capture_output=True, text=True).stdout.strip() or 0)


def lufs(p, extra=[]):
    e = subprocess.run(["ffmpeg", "-v", "info", "-nostats"] + extra + ["-i", p, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    linie = [l for l in e.splitlines() if l.strip().startswith("I:")]
    return float(linie[-1].split()[1])


POD_GLOSEM = 12.0   # muzyka tyle dB ciszej niz lektor; 13.11 15:27 zalozyciel: "lekko podglosnij" (bylo 16)

if __name__ == "__main__":
    wej, muz, wyj = sys.argv[1:4]
    pod = float(sys.argv[4]) if len(sys.argv) > 4 else POD_GLOSEM
    l_glos, l_muz = lufs(wej), lufs(muz)
    g = 10 ** ((l_glos - pod - l_muz) / 20)
    bas = miks(wej, muz, wyj, round(g, 3))
    print(f"lektor {l_glos} LUFS, muzyka {l_muz} LUFS -> podklad x{g:.3f} ({pod} dB pod glosem), bas {bas}%")
    print("gotowe:", wyj)
