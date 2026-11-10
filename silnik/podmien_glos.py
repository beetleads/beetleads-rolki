#!/usr/bin/env python3
"""Wymienia sciezke dzwieku w gotowej rolce (obraz zostaje bez zmian).

Lancuch jest celowo krotki, zeby nie ruszac barwy glosu (10.11 20:49):
  surowy mix stereo -> klik OBSERWUJ -> wygaszenie konca -> JEDNO wzmocnienie.
Zadnego loudnorm, limitera ani przestrajania. Gdy wzmocnienie do -14 LUFS
podbiloby szczyt powyzej -1,3 dBFS, zostaje cichsza, ale czysta wersja.
"""
import json, pathlib, re, subprocess, sys

KLIK = "/home/claude/silnik5/klik.wav"


def dlugosc(p):
    return float(subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", p], capture_output=True, text=True).stdout)


def lufs_tp(p):
    w = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", p, "-af",
                        "ebur128=peak=true:framelog=quiet", "-f", "null", "/dev/null"],
                       capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", w)
    t = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", w)
    return float(i[-1]), float(t[-1])


def buduj(film, glos, spec, wyj, wzm=0.0):
    s = json.loads(pathlib.Path(spec).read_text())
    dl_v = dlugosc(film)
    ost = s["slowa"][-1]["do"]
    st = max(ost + 0.05, dl_v - 0.80)
    d = dl_v - st
    ms = int(s["klik_dzwiek"] * 1000)
    fg = (f"[2:a]adelay={ms}|{ms},volume=0.85[kl];"
          f"[1:a][kl]amix=inputs=2:duration=longest:normalize=0,"
          f"apad=pad_dur=1.0,atrim=0:{dl_v:.3f},"
          f"afade=t=out:st={st:.3f}:d={d:.3f}:curve=qsin,volume={wzm:.2f}dB[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", film, "-i", glos, "-i", KLIK,
                    "-filter_complex", fg, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", wyj], check=True)


def podmien(film, glos, spec, wyj, cel=-14.0):
    buduj(film, glos, spec, wyj)
    i, tp = lufs_tp(wyj)
    k = min(cel - i, -1.3 - tp)
    if abs(k) > 0.2:
        buduj(film, glos, spec, wyj, wzm=k)
    i, tp = lufs_tp(wyj)
    print(f"{pathlib.Path(wyj).name} | {i} LUFS | peak {tp} dBFS")


if __name__ == "__main__":
    podmien(*sys.argv[1:5])
