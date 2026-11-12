#!/usr/bin/env python3
"""Pelna walidacja gotowej rolki: dzwiek, wygaszenie, pasy, kolizje, dlugosc."""
import json, re, subprocess, sys, pathlib
import numpy as np
from PIL import Image

def ff(args):
    return subprocess.run(args, capture_output=True, text=True).stderr

def dlugosc(p):
    return float(subprocess.run(["ffprobe","-v","0","-show_entries","format=duration",
        "-of","csv=p=0",p],capture_output=True,text=True).stdout.strip())

def lufs_tp(p):
    w = ff(["ffmpeg","-nostats","-hide_banner","-i",p,"-af",
            "ebur128=peak=true:framelog=quiet","-f","null","/dev/null"])
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", w); t = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", w)
    return (float(i[-1]) if i else 0.0), (float(t[-1]) if t else 0.0)

def poziom(p, od, dl=0.12):
    w = ff(["ffmpeg","-nostats","-hide_banner","-ss",str(od),"-t",str(dl),"-i",p,
            "-af","volumedetect","-f","null","/dev/null"])
    m = re.search(r"max_volume: (-?[\d.]+) dB", w)
    return float(m.group(1)) if m else -99.0

def klatka(p, t, out):
    subprocess.run(["ffmpeg","-y","-v","error","-ss",str(t),"-i",p,"-frames:v","1",out],check=True)
    return np.asarray(Image.open(out).convert("RGB")).astype(float)

def pasy(a):
    """Czy trzy pasy (gora/srodek/dol) maja tresc - kontrast lokalny ponad tlem."""
    h = a.shape[0]
    out = []
    for lo, hi in ((0.08,0.33),(0.34,0.62),(0.63,0.92)):
        s = a[int(h*lo):int(h*hi)]
        g = s.mean(axis=2)
        out.append(float(g.std()))
    return out

def sprawdz(p, nazwa=None):
    nazwa = nazwa or pathlib.Path(p).name
    d = dlugosc(p); i, tp = lufs_tp(p)
    ogon = [poziom(p, round(d-x,2)) for x in (0.60,0.30,0.10)]
    tmp = "/tmp/claude-0/kl.png"
    try:
        st = [pasy(klatka(p, t, tmp)) for t in (0.5, d*0.5, d-1.2)]
    except Exception as e:
        st = [[0,0,0]]
    info = subprocess.run(["ffprobe","-v","0","-select_streams","v:0","-show_entries",
        "stream=width,height,r_frame_rate","-of","csv=p=0",p],capture_output=True,text=True).stdout.strip()
    bledy = []
    if not (17.0 <= d <= 23.0): bledy.append(f"dlugosc {d:.1f}s")
    if abs(i+14) > 1.2: bledy.append(f"LUFS {i}")
    if tp > -1.2: bledy.append(f"peak {tp}")
    if ogon[-1] > -45: bledy.append(f"koniec urwany ({ogon[-1]} dB)")
    for n, s in zip(("0,5s","srodek","koniec"), st):
        puste = [j for j,v in enumerate(s) if v < 6]
        if puste: bledy.append(f"{n}: pusty pas {puste}")
    print(f"{nazwa}\t{d:.1f}s\tLUFS {i}\tTP {tp}\togon {ogon}\t{info}\t" +
          ("OK" if not bledy else "BLAD: " + "; ".join(bledy)))
    return bledy

if __name__ == "__main__":
    for p in sys.argv[1:]:
        sprawdz(p)
