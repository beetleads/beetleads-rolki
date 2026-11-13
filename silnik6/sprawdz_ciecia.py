#!/usr/bin/env python3
"""Ciecia vs glos (13.11 22:28, Krzysztof: "sprawdzaj, czy zmiana kadru nie ucina glosu").
Dla kazdego ciecia obrazu sprawdza: (1) czy nie wypada w srodku slowa, (2) czy dzwiek nie ma dziury.
Dziura liczy sie tylko wtedy, gdy w surowym nagraniu lektora w tym miejscu jest glos.
Uzycie: sprawdz_ciecia.py film.mp4 spec.json [glos.wav]"""
import json, re, subprocess, sys

def ciecia(p):
    w = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-vf", "select='gt(scene,0.25)',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", w)]

def rms(p, od, dl):
    w = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-ss", f"{max(0,od):.3f}", "-t", f"{dl:.3f}", "-i", p,
                        "-af", "volumedetect", "-vn", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"mean_volume: (-?[\d.]+) dB", w)
    return float(m.group(1)) if m else -91.0

film, spec = sys.argv[1], sys.argv[2]
glos = sys.argv[3] if len(sys.argv) > 3 else None
# 13.11 23:30: sprawdzamy prawdziwe ciecia z montazu (zapisane przez hybryda.py), nie skoki animacji
lista = json.load(open(spec)).get("ciecia")
slowa = json.load(open(spec))["slowa"]
bledy = 0
for t in (lista if lista else ciecia(film)):
    w_slowie = [s["s"] for s in slowa if s["od"] + 0.06 < t < s["do"] - 0.06]
    przed, w, po = rms(film, t - 0.35, 0.25), rms(film, t - 0.04, 0.08), rms(film, t + 0.1, 0.25)
    dziura = w < min(przed, po) - 12
    if dziura and glos:
        dziura = rms(glos, t - 0.04, 0.08) > w + 12   # w lektorze jest glos, a w filmie cisza
    flaga = []
    if w_slowie: flaga.append("w srodku slowa '" + w_slowie[0] + "'")
    if dziura: flaga.append(f"dziura w dzwieku {w:.0f} dB")
    if flaga: bledy += 1
    print(f"ciecie {t:6.2f}s  {'; '.join(flaga) if flaga else 'ok'}")
print("CIECIA OK" if not bledy else f"CIECIA: {bledy} do poprawy")
