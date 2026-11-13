#!/usr/bin/env python3
"""Rolka hybrydowa: prawdziwe ujecia z Higgsfielda + animacje silnika 6 nalozone na nie
(12.11 23:43: "mix higgsfield i silnik pod wzgledem efektow i przedstawionych animacji").

- scena pytania: jasne ujecie + pytanie u gory na ciemnym pasie (hak),
- sceny mechanizmu/dowodu/wniosku: ujecie przyciemnione i lekko rozmyte, a na nim animacja
  silnika 6 pomniejszona (skala, kotwica u gory), zeby zostalo miejsce na napisy wyzej,
- CTA: rozmyte ujecie + koncowka silnika 6,
- efekty: najazd na starcie, punch-zoom i rozszczepienie RGB na cieciach, blysk, dryf,
  wstrzas na liczbie dowodu, winieta, smuga. Bez dzwiekow na cieciach.

Uzycie: python3 hybryda.py hyb_<kod>.json wyj_raw.mp4
"""
import sys, json, pathlib, subprocess, shutil, random
import numpy as np
import silnik6 as s6
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

W, H, CX, FPS = s6.W, s6.H, s6.CX, s6.FPS
cfg = json.loads(pathlib.Path(sys.argv[1]).read_text())
wyj = sys.argv[2]
r = json.loads(pathlib.Path(cfg["rolka"]).read_text())
slowa = json.load(open(r["slowa"]))
akc = s6.hexk(r.get("akcent", "#35D0E8"))
s6.CAP_Y = cfg.get("cap_y", 1200)
DL = round(slowa[-1]["do"] + 0.6, 2)


def czas_slowa(spec):
    tekst, _, nr = spec.partition("#")
    nr, k = int(nr or 1), 0
    for s in slowa:
        if s["s"].strip(".,?!:„”").lower() == tekst.lower():
            k += 1
            if k == nr:
                return s["od"]
    raise SystemExit(f"nie ma slowa '{spec}'")


sceny = []
for sc in r["sceny"]:
    sceny.append([0.0 if sc.get("od") == 0 else czas_slowa(sc["od"]) - 0.08, sc])
for i, s in enumerate(sceny):
    s.append(sceny[i + 1][0] if i + 1 < len(sceny) else DL)
assert len(cfg["tla"]) == len(sceny), "tla: po jednym ujeciu na scene"
# tla[i]: jedno ujecie albo lista ujec dla sceny i (kolejne z "od": slowo = podciecie w scenie)
SEGM = []   # (od, do, cfg_ujecia, nr_sceny)
for i, ((od, sc, do), tl) in enumerate(zip(sceny, cfg["tla"])):
    lst = tl if isinstance(tl, list) else [tl]
    pocz = [od] + [czas_slowa(u["od"]) - 0.08 for u in lst[1:]]
    for j, u in enumerate(lst):
        SEGM.append((pocz[j], pocz[j + 1] if j + 1 < len(lst) else do, u, i))
CIECIA = [s[0] for s in SEGM[1:]]
T_CTA = next(s[0] for s in sceny if s[1]["typ"] == "cta")

kat = pathlib.Path(wyj).with_suffix(".klatki")
if kat.exists():
    shutil.rmtree(kat)
kat.mkdir()
klatki = []
for i, (od, do, tl, _) in enumerate(SEGM):
    d = kat / f"seg{i}"
    d.mkdir()
    f = (do - od) / tl["dl"]
    eq = tl.get("eq", "eq=contrast=1.06:saturation=1.08")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(tl["st"]), "-t", str(tl["dl"]), "-i", tl["plik"], "-vf",
                    f"setpts={f:.4f}*PTS,fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920," + eq,
                    str(d / "f%05d.jpg")], check=True)
    klatki.append(sorted(d.glob("f*.jpg")))


def zoom(im, z, dx=0, dy=0):
    w, h = int(W * z), int(H * z)
    x0, y0 = (w - W) // 2 + dx, (h - H) // 2 + dy
    return im.resize((w, h), Image.BICUBIC).crop((x0, y0, x0 + W, y0 + H))


def rgb_split(im, px):
    r_, g, b, a = im.split()
    return Image.merge("RGBA", (ImageChops.offset(r_, px, 0), g, ImageChops.offset(b, -px, 0), a))


_yy, _xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2)
WIN = Image.new("RGBA", (W, H), (0, 0, 0, 0))
WIN.putalpha(Image.fromarray((np.clip((_r - 0.75) / 0.6, 0, 1) ** 1.6 * 150).astype(np.uint8)))
CY = s6.CAP_Y
PAS = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(PAS).rectangle([0, CY - 120, W, CY + 150], fill=(6, 6, 10, 150))
PAS = PAS.filter(ImageFilter.GaussianBlur(50))
GORA = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(GORA).rectangle([0, 200, W, 560], fill=(6, 6, 10, 150))
GORA = GORA.filter(ImageFilter.GaussianBlur(60))


def warstwa_sceny(sc, t, od, do):
    ws = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kt = {"akcent": akc, "czas_slowa": czas_slowa, "od": od}
    s6.SCENY[sc["typ"]](ws, min(t, do) - od, do - od, sc, kt)
    sk = cfg.get("skale", {}).get(sc["typ"], cfg.get("skala", 0.84))
    if sk != 1:
        w, h = int(W * sk), int(H * sk)
        mala = ws.resize((w, h), Image.LANCZOS)
        ws = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ky = cfg.get("kotwica_y", 250)
        ws.alpha_composite(mala, (int(CX - CX * sk), int(ky - ky * sk)))
    return ws


gr = s6.grupy(slowa)
T_SZOK = czas_slowa(cfg["wstrzas"]) if cfg.get("wstrzas") else None
random.seed(7)
n = int(DL * FPS)
for k in range(n):
    t = k / FPS
    g_i = max(j for j, s in enumerate(SEGM) if s[0] <= t or j == 0)
    s_od, _, tl_cfg, i = SEGM[g_i]
    od, sc, do = sceny[i]
    dt = t - s_od
    fr = klatki[g_i]
    im = Image.open(fr[min(int(dt * FPS), len(fr) - 1)]).convert("RGBA")
    # ruch kamery
    z, dx, dy = 1 + 0.035 * min(1, dt / 4), 0, 0
    if t < 0.9:
        z = 1 + 0.22 * (1 - t / 0.9) ** 2
    elif g_i > 0 and dt < 0.35:
        z = 1 + 0.14 * (1 - dt / 0.35) ** 2
    if T_SZOK and T_SZOK - 0.05 <= t < T_SZOK + 0.3:
        z, dx, dy = max(z, 1.04), random.randint(-14, 14), random.randint(-14, 14)
    im = zoom(im, z, dx, dy)
    # gradacja ujecia pod animacje
    ciemn, rozm = tl_cfg.get("ciemn", 0.42), tl_cfg.get("rozm", 5)
    if sc["typ"] == "cta":
        a = s6.wej(t, od, 0.3)
        im = im.filter(ImageFilter.GaussianBlur(int(2 + 18 * a)))
        im.alpha_composite(Image.new("RGBA", (W, H), (8, 8, 12, int(125 * a))))
    else:
        if rozm:
            im = im.filter(ImageFilter.GaussianBlur(rozm))
        if ciemn != 1:
            im = ImageEnhance.Brightness(im).enhance(ciemn)
    im.alpha_composite(WIN)
    s6.smuga(im, t)
    if t < T_CTA:
        im.alpha_composite(PAS)
    # tresc sceny
    if sc["typ"].startswith("pytanie"):
        im.alpha_composite(GORA)
        if cfg.get("pytanie_grafika", True):
            # 13.11 09:44 "na poczatku brakuje wizualizacji do slow" - pytanie razem z grafika silnika
            im.alpha_composite(warstwa_sceny(sc, t, od, do))
        else:
            s6.pytanie_u_gory(im, sc["linie"], t, 1.0, akc)
    elif sc["typ"] == "cta":
        s6.scena_cta(im, t - od, DL - od, sc, {"akcent": akc})
    else:
        im.alpha_composite(warstwa_sceny(sc, t, od, do))
    # poprzednia animacja gasnie 0,25 s na nowym ujeciu (jak przenikanie w silniku 6)
    if i > 0 and t - od < 0.25 and not sceny[i - 1][1]["typ"].startswith("pytanie"):
        po, ps, pd = sceny[i - 1]
        ws = warstwa_sceny(ps, t, po, pd)
        ws.putalpha(ws.getchannel("A").point(lambda v, f=1 - (t - od) / 0.25: int(v * f)))
        im.alpha_composite(ws)
    # efekty ciecia
    for c in CIECIA:
        if c <= t < c + 0.15:
            im = rgb_split(im, int(14 * (1 - (t - c) / 0.15)) + 1)
        if c - 0.04 <= t < c + 0.16:
            a = 1 - abs(t - (c + 0.03)) / 0.16
            im.alpha_composite(Image.new("RGBA", (W, H), (255, 248, 225, int(150 * max(0, a)))))
    for g in gr:
        if g[0]["od"] - 0.1 <= t <= g[-1]["do"] + 0.25:
            s6.napisy(im, g, t)
            break
    if t < T_CTA:
        s6.znak(im)
    im.convert("RGB").save(kat / f"k{k:05d}.jpg", quality=92)

subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(kat / "k%05d.jpg"), "-i", r["audio"],
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "60", "-c:a", "aac",
                "-b:a", "192k", "-movflags", "+faststart", "-shortest", wyj], check=True)
shutil.rmtree(kat)
cta = sceny[-1]
pathlib.Path(wyj).with_suffix(".spec.json").write_text(json.dumps(
    {"slowa": slowa, "klik_dzwiek": round(T_CTA + cta[1].get("klik", 0.9), 2)}, ensure_ascii=False))
print("gotowe:", wyj, n, "klatek; ciecia", [round(c, 2) for c in CIECIA])
