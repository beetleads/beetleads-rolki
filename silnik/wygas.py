#!/usr/bin/env python3
"""Wygaszenie dzwieku na koncu rolki (10.11 19:54: "na koniec przerwo ladowanie dzwieku").

Bierze gotowa rolke i czasy slow, wydluza obraz, wyciszy muzyke lagodnie po ostatnim
slowie lektora i wyrownuje poziom do -14 LUFS. Pilnuje, zeby ostatnie 0,5 s zjechalo
ponizej -25 dB - jesli nie, wydluza ogon i powtarza (zlapane na rolce "gratis":
ostatnie slowo konczylo sie tak pozno, ze fade mial ledwie 0,35 s i bylo slyszalne ciecie).
"""
import json, subprocess, sys, pathlib, re

def dlugosc(p):
    return float(subprocess.run(["ffprobe","-v","0","-show_entries","format=duration",
        "-of","csv=p=0",p],capture_output=True,text=True).stdout.strip())

def szczyt(p, od):
    w = subprocess.run(["ffmpeg","-nostats","-hide_banner","-ss",str(od),"-i",p,
        "-af","volumedetect","-f","null","/dev/null"],capture_output=True,text=True).stderr
    m = re.search(r"max_volume: (-?[\d.]+) dB", w)
    return float(m.group(1)) if m else 0.0

def lufs(p):
    w = subprocess.run(["ffmpeg","-nostats","-hide_banner","-i",p,"-af",
        "ebur128=framelog=quiet","-f","null","/dev/null"],capture_output=True,text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", w)
    return float(m[-1]) if m else 0.0

def wygas(wej, slowa_json, wyj, ogon=0.45, klik=None, korekta=0.0):
    ost = json.load(open(slowa_json))[-1]["do"]
    dl = dlugosc(wej)
    nowa = dl + ogon
    st = max(ost + 0.05, dl - 0.10)
    d = nowa - st
    a = (f"[1:a]apad=pad_dur=0.6,atrim=0:{nowa:.3f},"
         f"afade=t=out:st={st:.3f}:d={d:.3f}:curve=qsin,volume={korekta:.2f}dB[a]")
    wejscia = ["-i",wej,"-i",wej]
    fg = f"[0:v]tpad=stop_mode=clone:stop_duration={ogon}[v];" + a
    subprocess.run(["ffmpeg","-y","-v","error",*wejscia,"-filter_complex",fg,
        "-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","19",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",wyj],check=True)
    return st, d

def popraw(wej, slowa_json, wyj, cel=-14.0):
    """Dwa przebiegi: najpierw fade, potem korekta poziomu; ogon rosnie az ucichnie."""
    ogon = 0.45
    for _ in range(4):
        wygas(wej, slowa_json, wyj, ogon=ogon)
        d = dlugosc(wyj)
        if szczyt(wyj, max(0, d - 0.5)) <= -25.0:
            break
        ogon += 0.25
    k = cel - lufs(wyj)
    if abs(k) > 0.3:
        wygas(wej, slowa_json, wyj, ogon=ogon, korekta=k)
    print(pathlib.Path(wyj).name, "ogon", round(ogon,2), "LUFS", lufs(wyj),
          "ostatnie 0,5 s", szczyt(wyj, max(0, dlugosc(wyj)-0.5)), "dB")

if __name__ == "__main__":
    popraw(sys.argv[1], sys.argv[2], sys.argv[3])
