#!/usr/bin/env python3
"""Ostatni przebieg po renderze: klikniecie OBSERWUJ, wygaszenie konca, poziom -14 LUFS.

Zasady, ktore ten skrypt trzyma za mnie:
  - zaden dzwiek przy zmianie ujecia; jedyny efekt to klik przycisku follow
  - dzwiek na koncu WYGASA, nie urywa sie (10.11 19:54)
  - -14 LUFS (+-1), true peak <= -1,3 dBFS
"""
import json, re, subprocess, sys, pathlib

KLIK = "/home/claude/silnik5/klik.wav"


def dlugosc(p):
    return float(subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())


def lufs_tp(p):
    w = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", p, "-af",
                        "ebur128=peak=true:framelog=quiet", "-f", "null", "/dev/null"],
                       capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", w)
    t = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", w)
    return (float(i[-1]) if i else 0.0), (float(t[-1]) if t else 0.0)


def poziom(p, od, dl=0.12):
    w = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-ss", str(od), "-t", str(dl),
                        "-i", p, "-af", "volumedetect", "-f", "null", "/dev/null"],
                       capture_output=True, text=True).stderr
    m = re.search(r"max_volume: (-?[\d.]+) dB", w)
    return float(m.group(1)) if m else 0.0


def przebieg(wej, spec, wyj, ogon, korekta=0.0, limiter=False):
    s = json.loads(pathlib.Path(spec).read_text())
    ost = s["slowa"][-1]["do"]
    dl = dlugosc(wej)
    nowa = dl + ogon
    st = max(ost + 0.05, dl - 0.80)        # fade moze wejsc na ogon ostatniego slowa
    d = nowa - st
    klik_t = s.get("klik_dzwiek")
    we = ["-i", wej, "-i", wej]
    mix = "[1:a]"
    if klik_t:
        we += ["-i", KLIK]
        ms = int(klik_t * 1000)
        mix = (f"[2:a]adelay={ms}|{ms},volume=0.85[kl];"
               f"[1:a][kl]amix=inputs=2:duration=longest:normalize=0,")
        mix = mix[:-1] + "[sum];[sum]"
    fg = (f"[0:v]tpad=stop_mode=clone:stop_duration={ogon}[v];" + mix +
          f"apad=pad_dur=0.6,atrim=0:{nowa:.3f},"
          f"afade=t=out:st={st:.3f}:d={d:.3f}:curve=qsin,volume={korekta:.2f}dB"
          + (",alimiter=limit=0.80:level=disabled" if limiter else "") + "[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *we, "-filter_complex", fg,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "19", "-pix_fmt", "yuv420p", "-g", "60",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", wyj], check=True)
    return st, d


def finisz(wej, spec, wyj, cel=-14.0):
    """Fade + klik, a potem loudnorm w dwoch przebiegach.

    10.11 20:20: samo `volume` nie dowozi -14 LUFS - przy szczycie blisko 0 dBFS wzmocnienie
    trzeba bylo sciac do ok. -1,3 dB i rolki konczyly na -17,5 do -19 LUFS. `loudnorm` z
    pomiarem (measured_*) podnosi glosnosc i pilnuje true peaku jednoczesnie.
    """
    ogon = 0.45
    przebieg(wej, spec, wyj, ogon)
    i, tp = lufs_tp(wyj)
    k = min(cel - i, -1.35 - tp)          # ZERO loudnorm - jedno zmierzone wzmocnienie
    if abs(k) > 0.2:
        przebieg(wej, spec, wyj, ogon, korekta=k)
        i, tp = lufs_tp(wyj)
    if i < cel - 0.6 or tp > -1.3:
        # UWAGA: `przebieg` liczy od surowego pliku, wiec wzmocnienie musi byc SUMA
        # dotychczasowego `k` i brakujacych decybeli - inaczej drugi gain gubi pierwszy
        # (zlapane 10.11 na rolce "rozrzut": konczyla na -15,1 LUFS).
        # 11.11: z wlaczonym limiterem szczyt trzyma filtr, wiec wzmocnienie dobieramy
        # iteracyjnie pod GLOSNOSC, a true peak tylko sprawdzamy. Kodek AAC potrafi
        # przestrzelic szczyt ponad wynik filtra (rolka "bon": -1,35 liczone, -0,8 zmierzone).
        for _ in range(4):
            k = k + (cel - i)
            przebieg(wej, spec, wyj, ogon, korekta=k, limiter=True)
            i, tp = lufs_tp(wyj)
            if abs(i - cel) <= 0.5 and tp <= -1.3:
                break
    assert abs(i - cel) <= 1.0, f"glosnosc {i} LUFS poza -14 +-1"
    assert tp <= -1.2, f"true peak {tp} dBFS ponad limit"
    d = dlugosc(wyj)
    zjazd = [poziom(wyj, round(d - x, 2)) for x in (0.90, 0.60, 0.40, 0.20, 0.08)]
    i, tp = lufs_tp(wyj)
    print(pathlib.Path(wyj).name, f"LUFS {i} TP {tp} zjazd {zjazd}")
    assert zjazd[-1] < -60, "koncowka nie wycisza sie do ciszy"
    return wyj


if __name__ == "__main__":
    finisz(sys.argv[1], sys.argv[2], sys.argv[3])
