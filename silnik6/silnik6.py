#!/usr/bin/env python3
"""SILNIK 6 - rolka jako animowane wyjasnienie (12.11, zalozyciel 11:01).

Format w jednym zdaniu: pytanie, ktore ludzie sami zadaja -> animacja, ktora
pokazuje mechanizm tak prosto, jak dla pieciolatka -> jeden dowod -> CTA
"Zaobserwuj profil po wiecej ciekawostek".

Zasady wbudowane w kod (nie w pamiec):
  - jedna rzecz na ekranie naraz: animacja w gornej czesci, napisy pod nia,
    nic poza tym (bez kart "Na start", "Proba badania", chipow, slupkow-wypelniaczy);
  - scena startuje na konkretnym slowie lektora, wiec obraz nigdy nie wyprzedza
    glosu (11:01: "za szybko jest wstep, nie da sie zrozumiec");
  - pierwsza klatka jest gotowa okladka: pytanie + obraz problemu w 0 s;
  - tlo spokojne: gradient z wolnym oddechem swiatla, zero drgan;
  - strefy bezpieczne: gora od 240 px (pasek TikToka), dol do 1560 px (opis),
    prawy pas ikon wolny - tresc w x 110..900.
  - kazdy element mierzy swoj tekst i sam sie zmniejsza, zanim wejdzie na sasiada.

Uzycie:  python3 silnik6.py rolka.json wyjscie_raw.mp4
"""
import json, math, sys, pathlib, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
X0, X1 = 110, 900                 # strefa tresci (prawy pas ikon TikToka wolny)
CX = (X0 + X1) // 2               # os kompozycji
CAP_Y = 1420                      # napisy pod animacja
BIEL = (255, 255, 255)
CIEMNY = (20, 17, 14)
ZOLTY = (255, 216, 77)
CZERW = (255, 72, 66)
ZIELONY = (64, 214, 120)
SZARY = (150, 152, 160)
FONTY = pathlib.Path(__file__).parent / "fonty"


def f_anton(px):
    return ImageFont.truetype(str(FONTY / "Anton.ttf"), int(px))


def f_inter(px, bold=True):
    return ImageFont.truetype(str(FONTY / ("Inter-Bold.ttf" if bold else "Inter-SemiBold.ttf")), int(px))


def hexk(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def szer(d, t, f):
    l, _, r, _ = d.textbbox((0, 0), t, font=f)
    return r - l


def dopasuj(d, t, maks_w, px, mini, fn=f_inter):
    f = fn(px)
    while szer(d, t, f) > maks_w and px > mini:
        px -= 2
        f = fn(px)
    return f


# ------------------------------------------------------------- krzywe ruchu

def wej(t, start=0.0, dl=0.35):
    """0..1 z miekkim wyhamowaniem (ease-out cubic)."""
    p = min(1.0, max(0.0, (t - start) / dl))
    return 1 - (1 - p) ** 3


def pop(t, start=0.0, dl=0.4):
    """Skala z lekkim przeskokiem: 0 -> 1.08 -> 1."""
    p = min(1.0, max(0.0, (t - start) / dl))
    if p <= 0:
        return 0.0
    return 1 + 0.08 * math.sin(math.pi * p) if p < 1 else 1.0


def mieszaj(a, b, p):
    return tuple(int(a[i] + (b[i] - a[i]) * p) for i in range(3))


# ------------------------------------------------------------- tlo

def tlo(t, akcent):
    """Spokojny gradient + jedno miekkie swiatlo, ktore oddycha bardzo wolno."""
    im = Image.new("RGBA", (W, H), (16, 16, 20, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 8):
        k = y / H
        d.rectangle([0, y, W, y + 8], fill=(int(16 + 10 * k), int(16 + 8 * k), int(22 + 6 * k), 255))
    sw = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sw)
    r = 520 + 30 * math.sin(t * 0.5)
    cy = 760 + 20 * math.sin(t * 0.33)
    ds.ellipse([CX - r, cy - r, CX + r, cy + r], fill=akcent + (34,))
    im.alpha_composite(sw.filter(ImageFilter.GaussianBlur(160)))
    return im


# ------------------------------------------------------------- prymitywy

def warstwa():
    nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return nak, ImageDraw.Draw(nak)


def pigulka(d, cx, y, tekst, f, tlo_k, tekst_k, obrys=None, pad=(24, 12)):
    w = szer(d, tekst, f) + 2 * pad[0]
    h = f.size + 2 * pad[1]
    d.rounded_rectangle([cx - w // 2, y, cx + w // 2, y + h], radius=h // 2, fill=tlo_k,
                        outline=obrys, width=3 if obrys else 0)
    d.text((cx - w // 2 + pad[0], y + pad[1] - f.size * 0.08), tekst, font=f, fill=tekst_k)
    return w, h


def telefon(im, cx, cy, skala, a, ekran_fn, t):
    """Telefon z ekranem; ekran_fn(d, box, t) rysuje zawartosc."""
    w, h = int(380 * skala), int(760 * skala)
    x0, y0 = cx - w // 2, cy - h // 2
    nak, d = warstwa()
    d.rounded_rectangle([x0 + 10, y0 + 18, x0 + w + 10, y0 + h + 18], radius=int(58 * skala), fill=(0, 0, 0, int(110 * a)))
    nak = nak.filter(ImageFilter.GaussianBlur(18))
    d = ImageDraw.Draw(nak)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(58 * skala), fill=(34, 34, 40, int(255 * a)))
    m = int(16 * skala)
    box = [x0 + m, y0 + m, x0 + w - m, y0 + h - m]
    d.rounded_rectangle(box, radius=int(44 * skala), fill=(246, 244, 240, int(255 * a)))
    d.rounded_rectangle([cx - int(50 * skala), y0 + m + 10, cx + int(50 * skala), y0 + m + int(34 * skala)],
                        radius=12, fill=(34, 34, 40, int(255 * a)))
    im.alpha_composite(nak)
    if a > 0.05:
        ekran_fn(im, box, t, a)
    return box


_foto_cache = {}


def foto(plik, w, h):
    k = (plik, w, h)
    if k not in _foto_cache:
        z = Image.open(plik).convert("RGB")
        s = max(w / z.width, h / z.height)
        z = z.resize((int(z.width * s) + 1, int(z.height * s) + 1))
        l, g = (z.width - w) // 2, (z.height - h) // 2
        _foto_cache[k] = z.crop((l, g, l + w, g + h)).convert("RGBA")
    return _foto_cache[k]


def plakietka(im, x, y, tekst, kol, skala_pop, a):
    """Czerwona plakietka typu 'Zostaly 3 szt.!' - pulsuje skala."""
    f = f_inter(34 * skala_pop)
    nak, d = warstwa()
    w = szer(d, tekst, f) + 40
    h = f.size + 26
    d.rounded_rectangle([x - w // 2, y - h // 2, x + w // 2, y + h // 2], radius=14, fill=kol + (int(255 * a),))
    d.text((x - w // 2 + 20, y - h // 2 + 10), tekst, font=f, fill=BIEL + (int(255 * a),))
    im.alpha_composite(nak)


def pudelko(d, x, y, s, a):
    """Karton magazynowy: bryla + tasma."""
    d.rectangle([x, y, x + s, y + s * 0.8], fill=(196, 150, 98, int(255 * a)), outline=(120, 86, 50, int(255 * a)), width=2)
    d.rectangle([x + s * 0.42, y, x + s * 0.58, y + s * 0.8], fill=(226, 196, 150, int(255 * a)))


def wtyczka(d, cx, cy, r, kol, a):
    """Klocek puzzla = wtyczka do sklepu."""
    k = kol + (int(255 * a),)
    d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=int(r * 0.25), fill=k)
    d.ellipse([cx - r * 0.28, cy - r * 1.42, cx + r * 0.28, cy - r * 0.86], fill=k)
    d.ellipse([cx + r * 0.86, cy - r * 0.28, cx + r * 1.42, cy + r * 0.28], fill=k)


def zuk(d, cx, cy, r, kol, a):
    """Prosty rysunek zuka (awatar beetleads): tulow, glowa, czulki, nogi, szew skrzydel."""
    k = kol + (int(255 * a),)
    for i in (-1, 0, 1):                       # nogi
        y = cy + i * r * 0.35
        d.line([cx - r * 0.5, y, cx - r * 0.95, y + r * 0.18 * i - r * 0.05], fill=k, width=max(3, int(r * 0.09)))
        d.line([cx + r * 0.5, y, cx + r * 0.95, y + r * 0.18 * i - r * 0.05], fill=k, width=max(3, int(r * 0.09)))
    d.line([cx - r * 0.12, cy - r * 0.78, cx - r * 0.45, cy - r * 1.05], fill=k, width=max(3, int(r * 0.07)))
    d.line([cx + r * 0.12, cy - r * 0.78, cx + r * 0.45, cy - r * 1.05], fill=k, width=max(3, int(r * 0.07)))
    d.ellipse([cx - r * 0.28, cy - r * 0.92, cx + r * 0.28, cy - r * 0.45], fill=k)
    d.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.85], fill=k)
    d.line([cx, cy - r * 0.45, cx, cy + r * 0.85], fill=(246, 244, 240, int(255 * a)), width=max(2, int(r * 0.06)))


def strzalka(d, a_xy, b_xy, kol, a, grub=8, postep=1.0, kreska=False, t=0.0):
    (x1, y1), (x2, y2) = a_xy, b_xy
    xe, ye = x1 + (x2 - x1) * postep, y1 + (y2 - y1) * postep
    if kreska:
        n = 18
        for i in range(n):
            p0 = (i / n + (t * 0.6) % (1 / n))
            p1 = p0 + 0.5 / n
            if p1 > postep:
                break
            d.line([x1 + (x2 - x1) * p0, y1 + (y2 - y1) * p0, x1 + (x2 - x1) * p1, y1 + (y2 - y1) * p1],
                   fill=kol + (int(255 * a),), width=grub)
    else:
        d.line([x1, y1, xe, ye], fill=kol + (int(255 * a),), width=grub)
    if postep >= 0.98:
        ang = math.atan2(y2 - y1, x2 - x1)
        L = grub * 3.2
        p1 = (x2 - L * math.cos(ang - 0.5), y2 - L * math.sin(ang - 0.5))
        p2 = (x2 - L * math.cos(ang + 0.5), y2 - L * math.sin(ang + 0.5))
        d.polygon([(x2, y2), p1, p2], fill=kol + (int(255 * a),))


def krzyzyk(d, cx, cy, r, a, p):
    k = CZERW + (int(255 * a),)
    if p > 0:
        q = min(1, p * 2)
        d.line([cx - r, cy - r, cx - r + 2 * r * q, cy - r + 2 * r * q], fill=k, width=16)
    if p > 0.5:
        q = (p - 0.5) * 2
        d.line([cx + r, cy - r, cx + r - 2 * r * q, cy - r + 2 * r * q], fill=k, width=16)


# ------------------------------------------------------------- sceny

def ekran_sklepu(liczba_fn, foto_plik):
    """Karta produktu w sklepie internetowym; liczba sztuk z funkcji czasu.
    Wszystkie wymiary skaluja sie z szerokoscia ekranu (k), zeby przy mniejszym
    telefonie cena nie wchodzila pod przycisk (12.11, wylapane na klatce)."""
    def rys(im, box, t, a):
        x0, y0, x1, y1 = box
        w = x1 - x0
        k = w / 378
        m = int(20 * k)
        fh = int(w * 0.9)
        ft = y0 + int(64 * k)
        im.alpha_composite(foto(foto_plik, w - 2 * m, fh), (x0 + m, ft))
        nak, d = warstwa()
        y = ft + fh + int(22 * k)
        d.rounded_rectangle([x0 + m + 4, y, x0 + int(w * 0.75), y + int(20 * k)], radius=8, fill=(40, 40, 46, int(220 * a)))
        d.rounded_rectangle([x0 + m + 4, y + int(34 * k), x0 + int(w * 0.5), y + int(50 * k)], radius=8, fill=(180, 180, 186, int(220 * a)))
        f = f_anton(52 * k)
        d.text((x0 + m + 4, y + int(62 * k)), "199 zł", font=f, fill=(30, 30, 34, int(255 * a)))
        bh = int(62 * k)
        d.rounded_rectangle([x0 + m + 4, y1 - bh - int(26 * k), x1 - m - 4, y1 - int(26 * k)], radius=int(18 * k), fill=(30, 30, 34, int(255 * a)))
        fb = f_inter(30 * k)
        tx = "Kup teraz"
        d.text(((x0 + x1) // 2 - szer(d, tx, fb) // 2, y1 - bh - int(26 * k) + (bh - fb.size) // 2 - 2), tx, font=fb, fill=BIEL + (int(255 * a),))
        im.alpha_composite(nak)
        assert y + int(62 * k) + f.size < y1 - bh - int(26 * k), "cena wchodzi pod przycisk"
        n = liczba_fn(t)
        puls = 1 + 0.06 * math.sin(t * 6.0)
        plakietka(im, (x0 + x1) // 2, ft + fh - int(30 * k), f"Zostały {n} szt.!", CZERW, puls * max(k, 0.85), a)
    return rys


def pytanie_u_gory(im, linie, t, a, akcent):
    nak, d = warstwa()
    fc = f_inter(28, False)
    pigulka(d, CX, 255, "PYTAJĄ LUDZIE", fc, (20, 20, 26, int(230 * a)), akcent + (int(255 * a),),
            obrys=akcent + (int(255 * a),), pad=(22, 8))
    y = 330
    for l in linie:
        f = dopasuj(d, l, X1 - X0, 64, 40, f_anton)
        d.text((CX - szer(d, l, f) // 2, y), l, font=f, fill=BIEL + (int(255 * a),))
        y += f.size + 10
    im.alpha_composite(nak)
    return y


def blysk(im, box, t):
    """Efekt otwarcia: od plakietki rozchodza sie dwie czerwone fale (0,2-1,2 s),
    a przez ekran telefonu przechodzi blysk (0,25-1,3 s)."""
    w = box[2] - box[0]
    k = w / 378
    bxc = (box[0] + box[2]) // 2
    byc = int(box[1] + 64 * k + 0.9 * w - 30 * k)
    for start in (0.2, 0.5):
        if start < t < start + 0.7:
            q = (t - start) / 0.7
            r = int(60 + 360 * q)
            nak, d = warstwa()
            d.ellipse([bxc - r, byc - r * 0.6, bxc + r, byc + r * 0.6], outline=CZERW + (int(220 * (1 - q)),), width=10)
            im.alpha_composite(nak)
    # smuga swiatla przez caly kadr (0,15-0,95 s) - efekt otwarcia widoczny w miniaturce feedu
    if 0.15 < t < 0.95:
        ps = (t - 0.15) / 0.8
        nak, d = warstwa()
        sx = int(-W * 0.7 + ps * W * 2.3)
        moc = int(150 * math.sin(math.pi * ps))
        for kk in range(6):
            d.line([sx + kk * 46, H, sx + kk * 46 + 700, 0], fill=(255, 255, 255, max(0, moc - kk * 18)), width=46)
        im.alpha_composite(nak.filter(ImageFilter.GaussianBlur(22)))
    if not 0.25 < t < 1.3:
        return
    pb = (t - 0.25) / 1.05
    nak, d = warstwa()
    bx = box[0] - 200 + pb * (box[2] - box[0] + 400)
    for kk in range(3):
        d.line([bx + kk * 30, box[3], bx + kk * 30 + 220, box[1]], fill=(255, 255, 255, int(130 * math.sin(math.pi * pb))), width=26)
    nak = nak.filter(ImageFilter.GaussianBlur(10))
    maska = Image.new("L", (W, H), 0)
    ImageDraw.Draw(maska).rounded_rectangle(box, radius=40, fill=255)
    nak.putalpha(Image.composite(nak.getchannel("A"), Image.new("L", (W, H), 0), maska))
    im.alpha_composite(nak)


def scena_pytanie(im, t, dl, p, kt):
    """Pytanie + telefon z plakietka; na slowie 'jutro' kartka DZIS -> JUTRO, a liczba dalej 3."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    if not p.get("jutro"):
        # pytanie bez "jutro": sam telefon na osi, z tym samym ozywieniem startu
        sk = 1.08 if t < 0.1 else 0.96 + 0.12 * (1 - (1 - min(1.0, (t - 0.1) / 0.7)) ** 3)
        box = telefon(im, CX, dol + 470, sk, 1.0, ekran_sklepu(lambda tt: 3, p["foto"]), t)
        blysk(im, box, t)
        return
    t_jutro = kt["czas_slowa"](p["jutro"]) - kt["od"]
    # OTWARCIE (efekt na starcie kazdej rolki): klatka 0 jest gotowa okladka,
    # a od 0,1 s telefon "wskakuje" blizej z przeskokiem, przez ekran przechodzi
    # blysk, a kalendarz wjezdza z prawej. Nic nie znika - wszystko tylko ozywa.
    if t < 0.1:
        sk, kal = 1.08, 1.0
    else:
        q = min(1.0, (t - 0.1) / 0.7)
        sk = 0.96 + 0.12 * (1 - (1 - q) ** 3) + 0.03 * math.sin(math.pi * q)
        kal = wej(t, 0.35, 0.45)
    box = telefon(im, CX - 130, dol + 470, sk, 1.0, ekran_sklepu(lambda tt: 3, p["foto"]), t)
    blysk(im, box, t)
    # kalendarz po prawej
    nak, d = warstwa()
    kx, ky = CX + 270 + int((1 - kal) * 340), dol + 380
    d.rounded_rectangle([kx - 110, ky - 120, kx + 110, ky + 120], radius=22, fill=(246, 244, 240, 255))
    d.rounded_rectangle([kx - 110, ky - 120, kx + 110, ky - 50], radius=22, fill=akc + (255,))
    d.rectangle([kx - 110, ky - 70, kx + 110, ky - 50], fill=akc + (255,))
    flip = wej(t, t_jutro, 0.35) if t_jutro > 0 else 0
    tekst = "JUTRO" if flip > 0.5 else "DZIŚ"
    fk = f_anton(56)
    sk = abs(math.cos(math.pi * flip))
    tw = szer(d, tekst, fk)
    d.text((kx - tw // 2, ky - 10 - int(30 * (1 - sk))), tekst, font=fk, fill=(30, 30, 34, int(255 * max(sk, 0.15))))
    im.alpha_composite(nak)
    if flip >= 1:
        nak, d = warstwa()
        pz = pop(t, t_jutro + 0.4, 0.4)
        if pz > 0:
            f = f_inter(36 * pz)
            pigulka(d, kx, ky + 150, "znowu 3?", f, ZOLTY + (255,), CIEMNY + (255,), pad=(20, 10))
        im.alpha_composite(nak)


def scena_magazyn(im, t, dl, p, kt):
    """Magazyn pelny kartonow po lewej, telefon z '3' po prawej, polaczenie przekreslone."""
    a = wej(t, 0, 0.4)
    nak, d = warstwa()
    mx, my = X0, 560
    d.rounded_rectangle([mx - 10, my - 60, mx + 300, my + 560], radius=24, fill=(28, 28, 34, int(235 * a)),
                        outline=(70, 70, 80, int(255 * a)), width=3)
    fl = f_inter(30)
    d.text((mx + 20, my - 40), "MAGAZYN", font=fl, fill=SZARY + (int(255 * a),))
    zgodnie = p.get("tryb") == "zgodnie"
    s = 78
    nr = 0
    ile_k = p["w_magazynie"] if zgodnie else 99
    for rz in range(6):
        for kol in range(3):
            pa = wej(t, 0.05 + nr * 0.03, 0.25)
            if pa > 0 and nr < ile_k:
                pudelko(d, mx + 20 + kol * (s + 10), my + 20 + rz * (s * 0.8 + 12) - int((1 - pa) * 40), s, pa * a)
            nr += 1
    fbig = f_anton(64)
    tl = f"{p['w_magazynie']} szt."
    d.text((mx + 145 - szer(d, tl, fbig) // 2, my + 590), tl, font=fbig, fill=BIEL + (int(255 * a),))
    im.alpha_composite(nak)
    telefon(im, X1 - 150, 880, 0.8, a, ekran_sklepu(lambda tt: 3, p["foto"]), t)
    nak, d = warstwa()
    pr = wej(t, 0.5, 0.6)
    kx = (mx + 315 + X1 - 310) // 2
    if zgodnie:
        # NORMALNIE: magazyn i napis sa polaczone - liczba na telefonie = kartony
        strzalka(d, (mx + 315, 880), (X1 - 310, 880), ZIELONY, a, grub=10, postep=pr, kreska=True, t=t)
        pk = wej(t, 1.0, 0.4)
        if pk > 0:
            d.ellipse([kx - 56, 824, kx + 56, 936], fill=ZIELONY + (int(255 * pk),))
            d.line([kx - 26, 880, kx - 6, 902, kx + 28, 858], fill=BIEL + (int(255 * pk),), width=12, joint="curve")
        im.alpha_composite(nak)
        return
    strzalka(d, (mx + 315, 880), (X1 - 310, 880), SZARY, a, grub=10, postep=pr, kreska=True, t=t)
    pk = wej(t, 1.2, 0.5)
    if pk > 0:
        d.ellipse([kx - 62, 818, kx + 62, 942], fill=(20, 20, 26, int(240 * pk)), outline=CZERW + (int(255 * pk),), width=6)
    krzyzyk(d, kx, 880, 34, a, pk)
    im.alpha_composite(nak)


def scena_wtyczka(im, t, dl, p, kt):
    """Wtyczka z suwakiem steruje liczba na telefonie - liczba idzie za suwakiem."""
    akc = kt["akcent"]
    a = wej(t, 0, 0.4)
    # suwak: 0-0.8 s stoi na 9, potem zjezdza do 3 i lekko 'oddycha'
    sl = 9 - 6 * wej(t, 0.8, 1.2)
    n = max(1, int(round(sl)))
    nak, d = warstwa()
    px, py = X0 + 170, 700
    if p.get("magazyn"):
        fm = f_inter(40)
        tm = p["magazyn"]
        wm, hm = pigulka(d, CX, 380, tm, fm, (28, 28, 34, int(240 * a)), SZARY + (int(255 * a),),
                         obrys=(70, 70, 80, int(255 * a)), pad=(22, 10))
        ps = wej(t, 0.6, 0.4)
        if ps > 0:
            d.line([CX - wm // 2 + 8, 380 + hm // 2, CX - wm // 2 + 8 + (wm - 16) * ps, 380 + hm // 2],
                   fill=CZERW + (int(255 * a),), width=7)
    wtyczka(d, px, py, 110 * pop(t, 0, 0.45), akc, a)
    fl = f_inter(34)
    d.text((px - szer(d, "WTYCZKA", fl) // 2, py + 150), "WTYCZKA", font=fl, fill=BIEL + (int(255 * a),))
    # panel ustawien
    gx, gy = X0, 960
    d.rounded_rectangle([gx, gy, gx + 380, gy + 230], radius=22, fill=(246, 244, 240, int(255 * a)))
    fs = f_inter(28)
    d.text((gx + 24, gy + 20), "Pokaż klientom:", font=fs, fill=(40, 40, 46, int(255 * a)))
    fn = f_anton(64)
    d.text((gx + 24, gy + 62), f"{n} szt.", font=fn, fill=(30, 30, 34, int(255 * a)))
    d.rounded_rectangle([gx + 30, gy + 176, gx + 350, gy + 188], radius=6, fill=(200, 200, 206, int(255 * a)))
    hx = gx + 30 + (sl - 1) / 9 * 320
    d.rounded_rectangle([gx + 30, gy + 176, hx, gy + 188], radius=6, fill=akc + (int(255 * a),))
    d.ellipse([hx - 22, gy + 160, hx + 22, gy + 204], fill=akc + (int(255 * a),), outline=BIEL + (int(255 * a),), width=4)
    im.alpha_composite(nak)
    telefon(im, X1 - 150, 880, 0.8, a, ekran_sklepu(lambda tt: n, p["foto"]), t)
    nak, d = warstwa()
    strzalka(d, (gx + 390, gy + 100), (X1 - 310, 760), akc, a, grub=10, postep=wej(t, 0.3, 0.6), kreska=True, t=t)
    im.alpha_composite(nak)


def scena_firmy(im, t, dl, p, kt):
    """22 firmy sprzedajace takie wtyczki - wskakuja po kolei, licznik rosnie."""
    akc = kt["akcent"]
    ile = p["ile"]
    nak, d = warstwa()
    kol, s, gap = 6, 96, 22
    szer_s = kol * s + (kol - 1) * gap
    x0, y0 = CX - szer_s // 2, 640
    widac = 0
    for i in range(ile):
        pa = pop(t, 0.2 + i * 0.06, 0.3)
        if pa <= 0:
            continue
        widac += 1
        x = x0 + (i % kol) * (s + gap) + s // 2
        y = y0 + (i // kol) * (s + gap) + s // 2
        r = s * 0.42 * pa
        wtyczka(d, x, y, r * 0.75, akc, 1.0)
    fb = f_anton(150)
    tl = str(widac)
    d.text((CX - szer(d, tl, fb) // 2, 400), tl, font=fb, fill=BIEL + (255,))
    fl = f_inter(40)
    tl = p["podpis"]
    f2 = dopasuj(d, tl, X1 - X0, 40, 28)
    d.text((CX - szer(d, tl, f2) // 2, y0 + 4 * (s + gap) + 30), tl, font=f2, fill=ZOLTY + (255,))
    im.alpha_composite(nak)


def scena_wniosek(im, t, dl, p, kt):
    """Wniosek dla widza: napis na telefonie gasnie, wskakuje zielony ptaszek
    i haslo, co z tym zrobic (tu: nie musisz sie spieszyc)."""
    a = wej(t, 0, 0.35)
    zgas = wej(t, 0.3, 0.5)
    box = telefon(im, CX - 140, 860, 0.85, a, ekran_sklepu(lambda tt: 3, p["foto"]), t)
    if zgas > 0:
        nak, d = warstwa()
        d.rounded_rectangle(box, radius=38, fill=(14, 14, 17, int(150 * zgas)))
        im.alpha_composite(nak)
    nak, d = warstwa()
    pz = pop(t, 0.5, 0.45)
    if pz > 0:
        r = int(110 * pz)
        cx, cy = X1 - 130, 760
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ZIELONY + (255,))
        d.line([cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.38, cx + r * 0.5, cy - r * 0.35],
               fill=BIEL + (255,), width=max(6, int(r * 0.18)), joint="curve")
        for i, linia in enumerate(p["linie"]):
            f = dopasuj(d, linia, 330, 46, 28, f_anton)
            d.text((cx - szer(d, linia, f) // 2, cy + 150 + i * (f.size + 8)), linia, font=f, fill=BIEL + (255,))
    im.alpha_composite(nak)


def scena_cta(im, t, dl, p, kt):
    """Karta profilu, kursor naciska Obserwuj, przycisk zmienia sie na Obserwujesz."""
    akc = hexk("#FF5C28")       # CTA zawsze w kolorze marki
    a = wej(t, 0, 0.35)
    nak, d = warstwa()
    cy = 860
    d.rounded_rectangle([X0 + 20, cy - 220, X1 - 20, cy + 220], radius=36, fill=(28, 28, 34, int(240 * a)),
                        outline=(70, 70, 80, int(255 * a)), width=3)
    d.ellipse([CX - 80, cy - 190, CX + 80, cy - 30], fill=(246, 244, 240, int(255 * a)))
    logo = pathlib.Path(__file__).parent / "logo.png"
    fn = f_inter(44)
    d.text((CX - szer(d, "@beetleads", fn) // 2, cy - 10), "@beetleads", font=fn, fill=BIEL + (int(255 * a),))
    t_klik = p.get("klik", 0.9)
    klik = t >= t_klik
    by = cy + 70
    sc = 1 - 0.08 * math.sin(math.pi * min(1, max(0, (t - t_klik) / 0.2))) if t >= t_klik else 1
    bw, bh = int(360 * sc), int(96 * sc)
    kol = (60, 60, 68) if klik else akc
    d.rounded_rectangle([CX - bw // 2, by, CX + bw // 2, by + bh], radius=24, fill=kol + (int(255 * a),))
    tb = "Obserwujesz ✓" if klik else "Obserwuj"
    fb = f_inter(40)
    tb = tb.replace(" ✓", "")
    d.text((CX - szer(d, tb, fb) // 2, by + bh // 2 - 26), tb, font=fb, fill=BIEL + (int(255 * a),))
    fp = f_inter(36, False)
    tp = "po więcej ciekawostek"
    d.text((CX - szer(d, tp, fp) // 2, cy + 260), tp, font=fp, fill=ZOLTY + (int(255 * a),))
    # kursor-palec dojezdza do przycisku
    pk = wej(t, 0.2, max(0.2, t_klik - 0.2))
    fx, fy = CX + 260 - 200 * pk, by + 260 - 190 * pk
    zn = 1 - wej(t, t_klik + 0.15, 0.3)
    if zn > 0:
        rr = 30 + 26 * wej(t, t_klik, 0.3)
        d.ellipse([fx - rr, fy - rr, fx + rr, fy + rr], outline=(255, 255, 255, int(230 * a * zn)), width=6)
    im.alpha_composite(nak)
    nak, d = warstwa()
    zuk(d, CX, cy - 105, 58, (20, 20, 24), a)
    im.alpha_composite(nak)


SCENY = {"pytanie": scena_pytanie, "magazyn": scena_magazyn, "wtyczka": scena_wtyczka,
         "firmy": scena_firmy, "wniosek": scena_wniosek, "cta": scena_cta}


# ------------------------------------------------------------- napisy

def grupy(slowa, maks=4):
    g, b = [], []
    for i, s in enumerate(slowa):
        b.append(s)
        koniec = s["s"].rstrip()[-1:] in ".?!:,"
        pauza = i + 1 < len(slowa) and slowa[i + 1]["od"] - s["do"] > 0.25
        if koniec or pauza or len(b) == maks:
            g.append(b)
            b = []
    if b:
        g.append(b)
    return g


def napisy(im, grupa, t):
    nak, d = warstwa()
    odst = 14

    def lam(f):
        wiersze, biez, sz = [], [], 0
        for s in grupa:
            w = szer(d, s["s"], f) + 30
            if sz + w > X1 - X0 and biez:
                wiersze.append(biez)
                biez, sz = [], 0
            biez.append(s)
            sz += w + odst
        if biez:
            wiersze.append(biez)
        return wiersze
    # najpierw mniejsza czcionka (do 40), dopiero potem drugi wiersz - zeby nie
    # zostawalo samotne "z" w drugiej linii
    for px in range(50, 39, -2):
        f = f_inter(px)
        wiersze = lam(f)
        if len(wiersze) == 1:
            break
    if len(wiersze) > 1:
        f = f_inter(50)
        wiersze = lam(f)
    y = CAP_Y - (len(wiersze) * (f.size + 34)) // 2
    for wier in wiersze:
        sw = sum(szer(d, s["s"], f) + 30 + odst for s in wier) - odst
        x = CX - sw // 2
        for s in wier:
            w = szer(d, s["s"], f) + 30
            teraz = s["od"] - 0.05 <= t <= s["do"] + 0.05
            d.rounded_rectangle([x, y, x + w, y + f.size + 22], radius=12,
                                fill=(ZOLTY + (255,)) if teraz else (14, 14, 17, 215))
            d.text((x + 15, y + 6), s["s"], font=f, fill=(CIEMNY if teraz else BIEL) + (255,))
            x += w + odst
        y += f.size + 34
    im.alpha_composite(nak)


def znak(im):
    nak, d = warstwa()
    f = f_inter(24, False)
    d.text((CX - szer(d, "@beetleads", f) // 2, 1530), "@beetleads", font=f, fill=(255, 255, 255, 140))
    im.alpha_composite(nak)


# ------------------------------------------------------------- render

def renderuj(plik, wyj):
    r = json.loads(pathlib.Path(plik).read_text())
    slowa = json.load(open(r["slowa"]))
    akc = hexk(r.get("akcent", "#35D0E8"))
    dl = round(slowa[-1]["do"] + 0.6, 2)

    def czas_slowa(spec):
        # spec: "jutro" albo "jutro#2" (drugie wystapienie)
        tekst, _, nr = spec.partition("#")
        nr = int(nr or 1)
        k = 0
        for s in slowa:
            if s["s"].strip(".,?!:").lower() == tekst.lower():
                k += 1
                if k == nr:
                    return s["od"]
        raise SystemExit(f"nie ma slowa '{spec}' w transkrypcji")

    sceny = []
    for sc in r["sceny"]:
        od = 0.0 if sc.get("od") == 0 else czas_slowa(sc["od"]) - 0.08
        sceny.append([max(0.0, od), sc])
    for i, s in enumerate(sceny):
        s.append(sceny[i + 1][0] if i + 1 < len(sceny) else dl)
    gr = grupy(slowa)
    if "klik" in r:
        pass
    kat = pathlib.Path(wyj).with_suffix(".klatki")
    if kat.exists():
        shutil.rmtree(kat)
    kat.mkdir()
    n = int(dl * FPS)
    for k in range(n):
        t = k / FPS
        im = tlo(t, akc)
        PRZEJSCIE = 0.25
        for od, sc, do in sceny:
            if od <= t < do + PRZEJSCIE:
                kt = {"akcent": akc, "czas_slowa": czas_slowa, "od": od}
                ws = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                # scena, ktora sie konczy, zamraza sie w ostatniej chwili i gasnie
                SCENY[sc["typ"]](ws, min(t, do) - od, do - od, sc, kt)
                if t >= do:
                    al = ws.getchannel("A").point(lambda v, f=1 - (t - do) / PRZEJSCIE: int(v * f))
                    ws.putalpha(al)
                im.alpha_composite(ws)
        for g in gr:
            if g[0]["od"] - 0.1 <= t <= g[-1]["do"] + 0.25:
                napisy(im, g, t)
                break
        znak(im)
        im.convert("RGB").save(kat / f"k{k:05d}.jpg", quality=92)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(kat / "k%05d.jpg"),
                    "-i", r["audio"], "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                    "-pix_fmt", "yuv420p", "-g", "60", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", wyj], check=True)
    shutil.rmtree(kat)
    # spec dla finisz.py (fade, glosnosc, klik przy Obserwuj)
    cta = [s for s in sceny if s[1]["typ"] == "cta"]
    spec = {"slowa": slowa}
    if cta:
        spec["klik_dzwiek"] = round(cta[0][0] + cta[0][1].get("klik", 0.9), 2)
    pathlib.Path(wyj).with_suffix(".spec.json").write_text(json.dumps(spec, ensure_ascii=False))
    print("gotowe:", wyj, n, "klatek")


if __name__ == "__main__":
    renderuj(sys.argv[1], sys.argv[2])
