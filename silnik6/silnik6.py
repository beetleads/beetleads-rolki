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
    """Koncowka: sama nazwa profilu i przycisk Obserwuj, ktory sie klika.
    12.11 12:01 zalozyciel: "logo wywal na koncu, jest nieladne, po prostu nazwa
    i obserwuj" - bez awatara, bez rysunku zuka, bez ramki karty."""
    akc = hexk("#FF5C28")       # CTA zawsze w kolorze marki
    a = wej(t, 0, 0.35)
    nak, d = warstwa()
    cy = 700
    fn = f_anton(96)
    tn = "@beetleads"
    d.text((CX - szer(d, tn, fn) // 2, cy - 130), tn, font=fn, fill=BIEL + (int(255 * a),))
    t_klik = p.get("klik", 0.9)
    klik = t >= t_klik
    by = cy + 40
    sc = 1 - 0.08 * math.sin(math.pi * min(1, max(0, (t - t_klik) / 0.2))) if t >= t_klik else 1
    bw, bh = int(420 * sc), int(108 * sc)
    kol = (60, 60, 68) if klik else akc
    d.rounded_rectangle([CX - bw // 2, by, CX + bw // 2, by + bh], radius=28, fill=kol + (int(255 * a),))
    tb = "Obserwujesz" if klik else "Obserwuj"
    fb = f_inter(46)
    d.text((CX - szer(d, tb, fb) // 2, by + bh // 2 - 30), tb, font=fb, fill=BIEL + (int(255 * a),))
    fp = f_inter(36, False)
    tp = "po więcej ciekawostek"
    d.text((CX - szer(d, tp, fp) // 2, by + 150), tp, font=fp, fill=ZOLTY + (int(255 * a),))
    # kursor-palec dojezdza do przycisku i znika po kliknieciu
    pk = wej(t, 0.2, max(0.2, t_klik - 0.2))
    fx, fy = CX + 260 - 200 * pk, by + 260 - 200 * pk
    zn = 1 - wej(t, t_klik + 0.15, 0.3)
    if zn > 0:
        rr = 30 + 26 * wej(t, t_klik, 0.3)
        d.ellipse([fx - rr, fy - rr, fx + rr, fy + rr], outline=(255, 255, 255, int(230 * a * zn)), width=6)
    im.alpha_composite(nak)


# ============================================================= ikony (proste, czytelne z daleka)

def ik_mikrofon(d, cx, cy, r, kol, a):
    k = kol + (int(255 * a),)
    d.rounded_rectangle([cx - r * 0.38, cy - r, cx + r * 0.38, cy + r * 0.25], radius=int(r * 0.38), fill=k)
    d.arc([cx - r * 0.7, cy - r * 0.55, cx + r * 0.7, cy + r * 0.6], 0, 180, fill=k, width=max(4, int(r * 0.12)))
    d.line([cx, cy + r * 0.6, cx, cy + r * 0.95], fill=k, width=max(4, int(r * 0.12)))
    d.line([cx - r * 0.4, cy + r * 0.95, cx + r * 0.4, cy + r * 0.95], fill=k, width=max(4, int(r * 0.12)))


def ik_oko(d, cx, cy, r, kol, a, otwarcie=1.0):
    k = kol + (int(255 * a),)
    h = r * 0.62 * otwarcie
    d.ellipse([cx - r, cy - h, cx + r, cy + h], outline=k, width=max(5, int(r * 0.11)))
    if otwarcie > 0.3:
        d.ellipse([cx - r * 0.38, cy - r * 0.38, cx + r * 0.38, cy + r * 0.38], fill=k)
        d.ellipse([cx - r * 0.12, cy - r * 0.2, cx + r * 0.06, cy - r * 0.02], fill=(20, 20, 26, int(255 * a)))


def ik_lupa(d, cx, cy, r, kol, a):
    k = kol + (int(255 * a),)
    d.ellipse([cx - r * 0.75, cy - r * 0.75, cx + r * 0.35, cy + r * 0.35], outline=k, width=max(5, int(r * 0.16)))
    d.line([cx + r * 0.25, cy + r * 0.25, cx + r * 0.8, cy + r * 0.8], fill=k, width=max(6, int(r * 0.22)))


def ik_pinezka(d, cx, cy, r, kol, a):
    k = kol + (int(255 * a),)
    d.ellipse([cx - r * 0.6, cy - r, cx + r * 0.6, cy + r * 0.2], fill=k)
    d.polygon([(cx - r * 0.5, cy - r * 0.15), (cx + r * 0.5, cy - r * 0.15), (cx, cy + r)], fill=k)
    d.ellipse([cx - r * 0.22, cy - r * 0.62, cx + r * 0.22, cy - r * 0.18], fill=(20, 20, 26, int(255 * a)))


def ik_klik(d, cx, cy, r, kol, a, t):
    """Palec-klik: kolko z rozchodzaca sie fala."""
    k = kol + (int(255 * a),)
    d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35], fill=k)
    q = (t * 1.2) % 1.0
    rr = r * (0.4 + 0.6 * q)
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=kol + (int(255 * a * (1 - q)),), width=6)


def ik_ekspres(d, cx, cy, r, a):
    """Ekspres do kawy - produkt z reklamy."""
    d.rounded_rectangle([cx - r * 0.7, cy - r, cx + r * 0.7, cy + r], radius=int(r * 0.15), fill=(60, 60, 68, int(255 * a)))
    d.rectangle([cx - r * 0.5, cy - r * 0.75, cx + r * 0.5, cy - r * 0.35], fill=(200, 200, 206, int(255 * a)))
    d.rounded_rectangle([cx - r * 0.3, cy + r * 0.15, cx + r * 0.3, cy + r * 0.75], radius=int(r * 0.08), fill=(246, 244, 240, int(255 * a)))
    d.rectangle([cx - r * 0.12, cy - r * 0.35, cx + r * 0.12, cy + r * 0.1], fill=(40, 40, 46, int(255 * a)))


def ekran_reklamy(produkt="Ekspres do kawy", rabat="-30%"):
    """Ekran telefonu z postem-reklama w feedzie."""
    def rys(im, box, t, a):
        x0, y0, x1, y1 = box
        w = x1 - x0
        k = w / 378
        nak, d = warstwa()
        m = int(20 * k)
        y = y0 + int(70 * k)
        d.text((x0 + m, y), "Sponsorowane", font=f_inter(22 * k, False), fill=(120, 120, 128, int(255 * a)))
        y += int(36 * k)
        kart = [x0 + m, y, x1 - m, y + int(300 * k)]
        d.rounded_rectangle(kart, radius=int(18 * k), fill=(230, 228, 224, int(255 * a)))
        ik_ekspres(d, (kart[0] + kart[2]) // 2, (kart[1] + kart[3]) // 2, 95 * k, a)
        y = kart[3] + int(20 * k)
        d.text((x0 + m, y), produkt, font=f_inter(30 * k), fill=(30, 30, 34, int(255 * a)))
        fr = f_anton(48 * k)
        d.text((x0 + m, y + int(46 * k)), rabat, font=fr, fill=CZERW + (int(255 * a),))
        bh = int(62 * k)
        d.rounded_rectangle([x0 + m, y1 - bh - int(26 * k), x1 - m, y1 - int(26 * k)], radius=int(18 * k), fill=(30, 30, 34, int(255 * a)))
        fb = f_inter(28 * k)
        d.text(((x0 + x1) // 2 - szer(d, "Zobacz", fb) // 2, y1 - bh - int(26 * k) + (bh - fb.size) // 2 - 2), "Zobacz", font=fb, fill=BIEL + (int(255 * a),))
        im.alpha_composite(nak)
    return rys


def dymek(d, x, y, linie, a, kol=(246, 244, 240), ogon="lewo"):
    f = f_inter(34)
    w = max(szer(d, l, f) for l in linie) + 56
    h = len(linie) * (f.size + 12) + 40
    d.rounded_rectangle([x, y, x + w, y + h], radius=28, fill=kol + (int(255 * a),))
    if ogon == "lewo":
        d.polygon([(x + 30, y + h - 2), (x + 70, y + h - 2), (x + 18, y + h + 34)], fill=kol + (int(255 * a),))
    for i, l in enumerate(linie):
        d.text((x + 28, y + 20 + i * (f.size + 12)), l, font=f, fill=(30, 30, 34, int(255 * a)))
    return w, h


# ============================================================= sceny: podsluch

def scena_pytanie_dymek(im, t, dl, p, kt):
    """Pytanie u gory, rozmowa (dymek + mikrofon) po lewej, telefon z reklama po prawej."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    sk = 0.92 if t < 0.1 else 0.84 + 0.08 * (1 - (1 - min(1.0, (t - 0.1) / 0.7)) ** 3)
    box = telefon(im, X1 - 160, dol + 470, sk, 1.0, ekran_reklamy(*p.get("reklama", ["Ekspres do kawy", "-30%"])), t)
    blysk(im, box, t)
    nak, d = warstwa()
    pa = 1.0 if t < 0.1 else wej(t, 0.2, 0.4)
    dymek(d, X0, dol + 140, p["dymek"], pa)
    ik_mikrofon(d, X0 + 110, dol + 520, 70, ZOLTY, pa)
    # fale dzwieku przy mikrofonie
    for i in range(3):
        q = ((t * 0.9) + i / 3) % 1.0
        rr = 90 + 80 * q
        d.arc([X0 + 110 - rr, dol + 500 - rr, X0 + 110 + rr, dol + 500 + rr], 300, 60,
              fill=ZOLTY + (int(200 * pa * (1 - q)),), width=6)
    im.alpha_composite(nak)


def scena_aplikacje(im, t, dl, p, kt):
    """Siatka aplikacji przeczesywana lupa; wynik: nagrania rozmowy 0."""
    akc = kt["akcent"]
    nak, d = warstwa()
    fb = f_anton(110)
    licz = int(p["ile"] * min(1.0, t / 1.2))
    tl = f"{licz:,}".replace(",", " ")
    d.text((CX - szer(d, tl, fb) // 2, 300), tl, font=fb, fill=BIEL + (255,))
    fl = f_inter(36)
    d.text((CX - szer(d, "sprawdzonych aplikacji", fl) // 2, 440), "sprawdzonych aplikacji", font=fl, fill=SZARY + (255,))
    kol, s, gap = 6, 92, 22
    x0 = CX - (kol * s + (kol - 1) * gap) // 2
    y0 = 520
    kolory = [(255, 120, 90), (90, 170, 255), (120, 220, 140), (255, 200, 80), (190, 130, 255), (80, 210, 210)]
    lx = x0 + (t * 520) % (kol * (s + gap))
    ly = y0 + 2 * (s + gap)
    for i in range(24):
        pa = pop(t, 0.05 + i * 0.03, 0.25)
        if pa <= 0:
            continue
        x = x0 + (i % kol) * (s + gap)
        y = y0 + (i // kol) * (s + gap)
        sc = s * pa
        d.rounded_rectangle([x + (s - sc) / 2, y + (s - sc) / 2, x + (s + sc) / 2, y + (s + sc) / 2], radius=22,
                            fill=kolory[i % 6] + (255,))
    ik_lupa(d, lx + 40, ly, 80, BIEL, 1.0)
    # wynik
    pw = wej(t, kt["czas_slowa"](p["wynik_od"]) - kt["od"], 0.4)
    if pw > 0:
        yw = y0 + 4 * (s + gap) + 10
        d.rounded_rectangle([X0 + 30, yw, X1 - 30, yw + 150], radius=28, fill=(28, 28, 34, int(240 * pw)),
                            outline=CZERW + (int(255 * pw),), width=4)
        ik_mikrofon(d, X0 + 120, yw + 75, 46, BIEL, pw)
        d.line([X0 + 70, yw + 125, X0 + 170, yw + 25], fill=CZERW + (int(255 * pw),), width=10)
        ft = f_inter(40)
        d.text((X0 + 210, yw + 30), "nagrania rozmowy:", font=ft, fill=BIEL + (int(255 * pw),))
        d.text((X0 + 210, yw + 72), "0", font=f_anton(60), fill=CZERW + (int(255 * pw),))
    im.alpha_composite(nak)


def scena_zrodla(im, t, dl, p, kt):
    """Trzy zrodla danych wpadaja do reklamy: wyszukiwanie, klik, polozenie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    pozycje = [("szukasz", ik_lupa, p["slowa"][0]), ("klikasz", None, p["slowa"][1]), ("jesteś", ik_pinezka, p["slowa"][2])]
    cel = (X1 - 150, 860)
    for i, (etyk, ik, slowo) in enumerate(pozycje):
        ts = max(0.0, kt["czas_slowa"](slowo) - kt["od"] - 0.1)
        pa = wej(t, ts, 0.35)
        if pa <= 0:
            continue
        y = 520 + i * 230
        d.rounded_rectangle([X0, y, X0 + 330, y + 170], radius=28, fill=(28, 28, 34, int(240 * pa)),
                            outline=akc + (int(255 * pa),), width=4)
        if ik is None:
            ik_klik(d, X0 + 80, y + 85, 50, akc, pa, t)
        else:
            ik(d, X0 + 80, y + 85, 46, akc, pa)
        d.text((X0 + 140, y + 62), etyk, font=f_inter(40), fill=BIEL + (int(255 * pa),))
        strzalka(d, (X0 + 340, y + 85), (cel[0] - 140, cel[1] - 60 + i * 60), akc, pa, grub=8,
                 postep=wej(t, ts + 0.2, 0.5), kreska=True, t=t)
    im.alpha_composite(nak)
    ts0 = max(0.0, kt["czas_slowa"](p["slowa"][0]) - kt["od"] - 0.1)
    telefon(im, cel[0], cel[1], 0.62, wej(t, 0, 0.4), ekran_reklamy(*p.get("reklama", ["Ekspres do kawy", "-30%"])), t)
    nak, d = warstwa()
    fr = f_anton(64)
    d.text((CX - szer(d, "REKLAMA DLA CIEBIE", fr) // 2, 330), "REKLAMA DLA CIEBIE", font=fr, fill=BIEL + (int(255 * wej(t, 0, 0.3)),))
    im.alpha_composite(nak)


def scena_mikro_oko(im, t, dl, p, kt):
    """Mikrofon przekreslony (nie slucha) kontra oko (patrzy)."""
    akc = kt["akcent"]
    t_oko = kt["czas_slowa"](p["oko_od"]) - kt["od"]
    nak, d = warstwa()
    a = wej(t, 0, 0.35)
    lx, rx, y = CX - 200, CX + 200, 780
    d.ellipse([lx - 150, y - 150, lx + 150, y + 150], fill=(28, 28, 34, int(240 * a)))
    ik_mikrofon(d, lx, y - 10, 90, SZARY, a)
    pk = wej(t, 0.4, 0.4)
    if pk > 0:
        d.line([lx - 110, y + 110, lx - 110 + 220 * pk, y + 110 - 220 * pk], fill=CZERW + (255,), width=14)
    d.text((lx - szer(d, "nie słucha", f_inter(40)) // 2, y + 180), "nie słucha", font=f_inter(40), fill=SZARY + (int(255 * a),))
    po = wej(t, t_oko - 0.1, 0.4)
    if po > 0:
        sk = pop(t, t_oko - 0.1, 0.45)
        d.ellipse([rx - 150 * sk, y - 150 * sk, rx + 150 * sk, y + 150 * sk], fill=akc + (int(60 * po),),
                  outline=akc + (int(255 * po),), width=6)
        ik_oko(d, rx, y, 100 * sk, akc, po, otwarcie=min(1.0, po * 1.4))
        d.text((rx - szer(d, "patrzy", f_inter(44)) // 2, y + 180), "patrzy", font=f_inter(44), fill=akc + (int(255 * po),))
    im.alpha_composite(nak)


# ============================================================= sceny: incognito

def ik_incognito(d, cx, cy, r, kol, a):
    """Kapelusz + okulary - symbol trybu incognito."""
    k = kol + (int(255 * a),)
    d.rounded_rectangle([cx - r * 0.55, cy - r * 0.95, cx + r * 0.55, cy - r * 0.25], radius=int(r * 0.15), fill=k)
    d.rounded_rectangle([cx - r, cy - r * 0.3, cx + r, cy - r * 0.12], radius=int(r * 0.08), fill=k)
    for sx in (-1, 1):
        d.ellipse([cx + sx * r * 0.48 - r * 0.32, cy + r * 0.12, cx + sx * r * 0.48 + r * 0.32, cy + r * 0.62],
                  outline=k, width=max(4, int(r * 0.1)))
    d.line([cx - r * 0.16, cy + r * 0.34, cx + r * 0.16, cy + r * 0.34], fill=k, width=max(4, int(r * 0.08)))


def okno_przegladarki(d, x0, y0, x1, y1, a, ciemne=True):
    tlo_k = (40, 40, 48) if ciemne else (246, 244, 240)
    d.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=tlo_k + (int(255 * a),), outline=(80, 80, 90, int(255 * a)), width=3)
    d.rounded_rectangle([x0, y0, x1, y0 + 70], radius=26, fill=(60, 60, 70, int(255 * a)))
    d.rectangle([x0, y0 + 40, x1, y0 + 70], fill=(60, 60, 70, int(255 * a)))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([x0 + 24 + i * 34, y0 + 24, x0 + 46 + i * 34, y0 + 46], fill=c + (int(255 * a),))
    d.rounded_rectangle([x0 + 140, y0 + 18, x1 - 30, y0 + 52], radius=17, fill=(30, 30, 36, int(255 * a)))


def czlowiek(d, cx, cy, r, kol, a):
    k = kol + (int(255 * a),)
    d.ellipse([cx - r * 0.35, cy - r, cx + r * 0.35, cy - r * 0.3], fill=k)
    d.rounded_rectangle([cx - r * 0.55, cy - r * 0.2, cx + r * 0.55, cy + r * 0.8], radius=int(r * 0.35), fill=k)


def scena_pytanie_okno(im, t, dl, p, kt):
    """Pytanie u gory + okno przegladarki incognito z kapeluszem i okularami."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    sk = 1.0 if t < 0.1 else 0.9 + 0.1 * (1 - (1 - min(1.0, (t - 0.1) / 0.7)) ** 3)
    nak, d = warstwa()
    w, h = int(760 * sk), int(560 * sk)
    x0, y0 = CX - w // 2, dol + 120
    okno_przegladarki(d, x0, y0, x0 + w, y0 + h, 1.0)
    ik_incognito(d, CX, y0 + h // 2 + 30, 150 * sk, BIEL, 1.0)
    fl = f_inter(34)
    tl = p.get("napis", "Tryb incognito")
    d.text((CX - szer(d, tl, fl) // 2, y0 + h - 80), tl, font=fl, fill=SZARY + (255,))
    im.alpha_composite(nak)
    blysk(im, (x0, y0, x0 + w, y0 + h), t)


def scena_ludzie(im, t, dl, p, kt):
    """100 osob, z czego p['ile'] podswietlonych, z podpisem."""
    akc = kt["akcent"]
    nak, d = warstwa()
    ile = p["ile"]
    kol, krok = 10, 74
    x0 = CX - (kol * krok) // 2 + krok // 2
    y0 = 520
    zap = int(ile * min(1.0, max(0.0, (t - 0.3) / 1.2)))
    for i in range(100):
        x = x0 + (i % kol) * krok
        y = y0 + (i // kol) * 76
        pa = wej(t, 0.02 * (i // kol), 0.3)
        czlowiek(d, x, y, 30, akc if i < zap else (70, 70, 80), pa)
    fb = f_anton(120)
    tl = f"{zap} na 100"
    d.text((CX - szer(d, tl, fb) // 2, 300), tl, font=fb, fill=akc + (255,))
    f2 = dopasuj(d, p["podpis"], X1 - X0, 40, 28)
    d.text((CX - szer(d, p["podpis"], f2) // 2, y0 + 10 * 76 + 10), p["podpis"], font=f2, fill=BIEL + (int(255 * wej(t, 0.6, 0.4)),))
    im.alpha_composite(nak)


def scena_czyszczenie(im, t, dl, p, kt):
    """Na urzadzeniu: lista historii znika pod gumka. Podpis: twoje urzadzenie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    x0, y0, x1, y1 = X0 + 20, 420, X1 - 20, 1180
    okno_przegladarki(d, x0, y0, x1, y1, wej(t, 0, 0.3))
    fh = f_inter(34)
    d.text((x0 + 40, y0 + 100), "Historia", font=fh, fill=BIEL + (255,))
    gumka = min(1.0, max(0.0, (t - 0.5) / 1.4))
    for i in range(7):
        yy = y0 + 170 + i * 80
        widac = gumka < (i + 1) / 7
        if widac:
            d.rounded_rectangle([x0 + 40, yy, x0 + 90, yy + 46], radius=10, fill=(90, 90, 100, 255))
            d.rounded_rectangle([x0 + 110, yy + 6, x1 - 140 - (i % 3) * 60, yy + 40], radius=10, fill=(120, 120, 130, 255))
    if 0 < gumka < 1:
        gy = y0 + 170 + gumka * 7 * 80
        d.rounded_rectangle([x1 - 200, gy - 20, x1 - 60, gy + 50], radius=14, fill=akc + (255,))
    if gumka >= 1:
        f = f_inter(40)
        d.text((CX - szer(d, "wyczyszczone", f) // 2, (y0 + y1) // 2), "wyczyszczone", font=f, fill=akc + (255,))
    pl = f_inter(34, False)
    d.text((CX - szer(d, p["podpis"], pl) // 2, y1 + 30), p["podpis"], font=pl, fill=SZARY + (255,))
    im.alpha_composite(nak)


def scena_obserwatorzy(im, t, dl, p, kt):
    """Laptop na dole, linia danych w gore do trzech obserwatorow; kazdy zapala oko na swoim slowie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    lx, ly = CX, 1120
    d.rounded_rectangle([lx - 150, ly - 90, lx + 150, ly + 60], radius=16, fill=(60, 60, 70, 255))
    d.rounded_rectangle([lx - 190, ly + 60, lx + 190, ly + 84], radius=10, fill=(90, 90, 100, 255))
    ik_incognito(d, lx, ly - 20, 50, BIEL, 1.0)
    xs = [X0 + 110, CX, X1 - 110]
    for i, (naz, slowo) in enumerate(zip(p["nazwy"], p["slowa"])):
        ts = max(0.0, kt["czas_slowa"](slowo) - kt["od"] - 0.1)
        pa = wej(t, ts, 0.35)
        x, y = xs[i], 560
        strzalka(d, (lx + (i - 1) * 60, ly - 100), (x, y + 185), akc, max(pa, 0.25), grub=6,
                 postep=1.0, kreska=True, t=t)
        d.ellipse([x - 110, y - 110, x + 110, y + 110], fill=(28, 28, 34, 255), outline=(akc if pa > 0 else (70, 70, 80)) + (255,), width=5)
        ik_oko(d, x, y, 70, akc if pa > 0 else (90, 90, 100), 1.0, otwarcie=0.2 + 0.8 * pa)
        f = dopasuj(d, naz, 270, 34, 24)
        d.text((x - szer(d, naz, f) // 2, y + 130), naz, font=f, fill=BIEL + (255,))
    fb = f_anton(60)
    tl = p.get("tytul", "WIDZĄ WSZYSTKO")
    d.text((CX - szer(d, tl, fb) // 2, 300), tl, font=fb, fill=BIEL + (int(255 * wej(t, 0, 0.3)),))
    im.alpha_composite(nak)


def scena_dom_siec(im, t, dl, p, kt):
    """Wniosek: dom (domownik nie widzi) kontra siec (widzi)."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.35)
    lx, rx, y = CX - 200, CX + 200, 760
    # dom
    d.polygon([(lx - 130, y - 20), (lx, y - 140), (lx + 130, y - 20)], fill=(246, 244, 240, int(255 * a)))
    d.rectangle([lx - 105, y - 20, lx + 105, y + 120], fill=(246, 244, 240, int(255 * a)))
    czlowiek(d, lx, y + 60, 50, (40, 40, 46), a)
    pz = pop(t, 0.3, 0.4)
    if pz > 0:
        d.ellipse([lx + 60, y - 160, lx + 160, y - 60], fill=ZIELONY + (255,))
        d.line([lx + 85, y - 110, lx + 105, y - 88, lx + 138, y - 132], fill=BIEL + (255,), width=10, joint="curve")
    d.text((lx - szer(d, p["lewy"], f_inter(36)) // 2, y + 160), p["lewy"], font=f_inter(36), fill=BIEL + (int(255 * a),))
    # siec - globus
    pg = wej(t, 0.6, 0.4)
    if pg > 0:
        d.ellipse([rx - 120, y - 120, rx + 120, y + 120], outline=akc + (int(255 * pg),), width=8)
        d.ellipse([rx - 55, y - 120, rx + 55, y + 120], outline=akc + (int(255 * pg),), width=6)
        d.line([rx - 120, y, rx + 120, y], fill=akc + (int(255 * pg),), width=6)
        d.ellipse([rx + 50, y - 170, rx + 160, y - 60], fill=CZERW + (int(255 * pg),))
        ik_oko(d, rx + 105, y - 115, 40, BIEL, pg)
        d.text((rx - szer(d, p["prawy"], f_inter(36)) // 2, y + 160), p["prawy"], font=f_inter(36), fill=BIEL + (int(255 * pg),))
    im.alpha_composite(nak)


# ============================================================= sceny: regulamin

def dokument(d, x0, y0, x1, y1, a, linie=14, przesun=0.0, wyroznij=None, akc=(255, 216, 77)):
    """Kartka regulaminu z liniami tekstu; `wyroznij` = (indeks_linii, tekst) - zaznaczony zapis."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=(246, 244, 240, int(255 * a)))
    fh = f_inter(30)
    d.text((x0 + 36, y0 + 26), "REGULAMIN", font=fh, fill=(30, 30, 34, int(255 * a)))
    krok = 46
    for i in range(linie):
        yy = y0 + 90 + i * krok - int(przesun)
        if yy < y0 + 80 or yy > y1 - 40:
            continue
        if wyroznij and i == wyroznij[0]:
            d.rounded_rectangle([x0 + 24, yy - 8, x1 - 24, yy + 34], radius=8, fill=akc + (int(255 * a),))
            d.text((x0 + 36, yy - 4), wyroznij[1], font=f_inter(28), fill=(30, 30, 34, int(255 * a)))
        else:
            dl = (x1 - x0 - 72) * (0.55 + 0.4 * ((i * 37) % 10) / 10)
            d.rounded_rectangle([x0 + 36, yy + 6, x0 + 36 + dl, yy + 22], radius=6, fill=(170, 170, 178, int(255 * a)))


def scena_pytanie_dokument(im, t, dl, p, kt):
    """Pytanie + regulamin, ktory przewija sie sam, i odhaczone 'Akceptuje'."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, x1 = CX - 300, CX + 300
    y0, y1 = dol + 110, dol + 760
    przes = 0 if t < 0.1 else (t - 0.1) * 260
    dokument(d, x0, y0, x1, y1 - 120, 1.0, linie=40, przesun=przes)
    # pole akceptacji
    by = y1 - 100
    d.rounded_rectangle([x0, by, x1, by + 100], radius=20, fill=(28, 28, 34, 255), outline=akc + (255,), width=4)
    zazn = t < 0.1 or t > 0.9
    d.rounded_rectangle([x0 + 30, by + 26, x0 + 78, by + 74], radius=10, fill=(akc if zazn else (60, 60, 70)) + (255,))
    if zazn:
        d.line([x0 + 40, by + 50, x0 + 52, by + 64, x0 + 70, by + 36], fill=CIEMNY + (255,), width=7, joint="curve")
    d.text((x0 + 100, by + 30), "Akceptuję regulamin", font=f_inter(36), fill=BIEL + (255,))
    im.alpha_composite(nak)
    blysk(im, (x0, y0, x1, y1 - 120), t)


def scena_klauzula(im, t, dl, p, kt):
    """Regulamin przewija sie i zatrzymuje na ukrytym zapisie, ktory podswietla sie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    x0, x1, y0, y1 = X0 + 10, X1 - 10, 330, 1180
    t_stop = 1.2
    przes = min(t, t_stop) / t_stop * 46 * 6
    widac = t > t_stop
    dokument(d, x0, y0, x1, y1, wej(t, 0, 0.3), linie=30, przesun=przes,
             wyroznij=(13, p["zapis"]) if widac else None, akc=akc if widac else (170, 170, 178))
    if widac:
        pz = pop(t, t_stop, 0.4)
        yy = y0 + 90 + 13 * 46 - int(przes)
        d.rounded_rectangle([x0 + 10, yy - 22, x1 - 10, yy + 48], radius=12, outline=CZERW + (int(255 * min(1, pz)),), width=6)
    im.alpha_composite(nak)


def scena_czas(im, t, dl, p, kt):
    """Dwa paski czasu: ile trzeba czytac vs ile ludzie czytali."""
    akc = kt["akcent"]
    nak, d = warstwa()
    fb = f_anton(64)
    d.text((CX - szer(d, p["tytul"], fb) // 2, 330), p["tytul"], font=fb, fill=BIEL + (int(255 * wej(t, 0, 0.3)),))
    maks = max(p["trzeba"], p["czytali"])
    wiersze = [("potrzeba", p["trzeba"], p["trzeba_tekst"], SZARY), ("czytali", p["czytali"], p["czytali_tekst"], akc)]
    for i, (nazwa, wart, tekst, kol) in enumerate(wiersze):
        y = 560 + i * 280
        pa = wej(t, 0.2 + i * 0.6, 0.9)
        d.text((X0, y), nazwa, font=f_inter(38), fill=BIEL + (255,))
        d.rounded_rectangle([X0, y + 70, X1, y + 140], radius=20, fill=(40, 40, 48, 255))
        w = (X1 - X0) * wart / maks * pa
        if w > 8:
            d.rounded_rectangle([X0, y + 70, X0 + w, y + 140], radius=20, fill=kol + (255,))
        ft = f_anton(54)
        d.text((X1 - szer(d, tekst, ft), y - 8), tekst, font=ft, fill=kol + (int(255 * pa),))
    im.alpha_composite(nak)


def scena_sprawdz(im, t, dl, p, kt):
    """Wniosek: regulamin z dwoma zaznaczonymi sekcjami do sprawdzenia."""
    akc = kt["akcent"]
    nak, d = warstwa()
    x0, x1, y0, y1 = CX - 300, CX + 300, 380, 1180
    dokument(d, x0, y0, x1, y1, wej(t, 0, 0.3), linie=16)
    for i, (sek, ws) in enumerate(zip(p["sekcje"], [0.3, 0.8])):
        pz = pop(t, ws, 0.4)
        if pz <= 0:
            continue
        yy = y0 + 180 + i * 300
        d.rounded_rectangle([x0 - 30, yy, x1 + 30, yy + 120], radius=22, fill=ZIELONY + (255,))
        d.ellipse([x0, yy + 25, x0 + 70, yy + 95], fill=BIEL + (255,))
        d.line([x0 + 16, yy + 60, x0 + 30, yy + 76, x0 + 56, yy + 42], fill=ZIELONY + (255,), width=8, joint="curve")
        d.text((x0 + 100, yy + 30), sek, font=f_anton(56), fill=BIEL + (255,))
    im.alpha_composite(nak)


# ============================================================= sceny: banery zgod

def baner(d, x0, y0, x1, a, odmowa=False, skala=1.0, akc=(53, 208, 232)):
    """Baner zgod na dole ekranu: duzy 'Akceptuje wszystkie', maly 'ustawienia',
    opcjonalnie rowny przycisk 'Odrzuc'. Zwraca (wysokosc, box ustawien)."""
    k = skala
    h = int(330 * k)
    d.rounded_rectangle([x0, y0, x1, y0 + h], radius=int(24 * k), fill=(250, 250, 248, int(255 * a)))
    ft = f_inter(26 * k)
    d.text((x0 + 26 * k, y0 + 22 * k), "Ta strona używa ciasteczek", font=ft, fill=(30, 30, 34, int(255 * a)))
    for i in range(2):
        d.rounded_rectangle([x0 + 26 * k, y0 + (70 + i * 26) * k, x1 - (60 + i * 90) * k, y0 + (84 + i * 26) * k], radius=6,
                            fill=(190, 190, 196, int(255 * a)))
    by = y0 + 140 * k
    fb = f_inter(28 * k)
    if odmowa:
        sz = (x1 - x0 - 26 * k * 3) / 2
        d.rounded_rectangle([x0 + 26 * k, by, x0 + 26 * k + sz, by + 70 * k], radius=int(16 * k), fill=(60, 60, 68, int(255 * a)))
        d.rounded_rectangle([x1 - 26 * k - sz, by, x1 - 26 * k, by + 70 * k], radius=int(16 * k), fill=(60, 60, 68, int(255 * a)))
        d.text((x0 + 26 * k + sz / 2 - szer(d, "Odrzuć", fb) / 2, by + 18 * k), "Odrzuć", font=fb, fill=BIEL + (int(255 * a),))
        d.text((x1 - 26 * k - sz / 2 - szer(d, "Akceptuj", fb) / 2, by + 18 * k), "Akceptuj", font=fb, fill=BIEL + (int(255 * a),))
        us = None
    else:
        d.rounded_rectangle([x0 + 26 * k, by, x1 - 26 * k, by + 80 * k], radius=int(16 * k), fill=akc + (int(255 * a),))
        tl = "Akceptuję wszystkie"
        d.text(((x0 + x1) / 2 - szer(d, tl, fb) / 2, by + 22 * k), tl, font=fb, fill=CIEMNY + (int(255 * a),))
        fu = f_inter(20 * k, False)
        uy = by + 104 * k
        d.text(((x0 + x1) / 2 - szer(d, "ustawienia", fu) / 2, uy), "ustawienia", font=fu, fill=(150, 150, 158, int(255 * a)))
        us = ((x0 + x1) / 2, uy + 12 * k)
    return h, us


def scena_pytanie_baner(im, t, dl, p, kt):
    """Pytanie + telefon ze strona i banerem, w ktorym nie ma przycisku odmowy."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    sk = 1.0 if t < 0.1 else 0.9 + 0.1 * (1 - (1 - min(1.0, (t - 0.1) / 0.7)) ** 3)

    def ekran(im2, box, tt, a):
        x0, y0, x1, y1 = box
        nak, d = warstwa()
        for i in range(6):
            d.rounded_rectangle([x0 + 24, y0 + 80 + i * 50, x1 - 24 - (i % 3) * 50, y0 + 104 + i * 50], radius=8,
                                fill=(200, 200, 206, int(255 * a)))
        bk = (x1 - x0) / 520
        baner(d, x0 + 10, y1 - int(350 * bk) - 20, x1 - 10, a, skala=bk, akc=akc)
        im2.alpha_composite(nak)
    box = telefon(im, CX, dol + 480, 1.08 * sk, 1.0, ekran, t)
    blysk(im, box, t)


def scena_kafelki(im, t, dl, p, kt):
    """Siatka kafelkow (kazdy = p['na_kafelek'] banerow); zgodne z prawem na zielono."""
    nak, d = warstwa()
    n, ok = p["n"], p["ok"]
    kol, s, gap = 10, 62, 12
    x0 = CX - (kol * s + (kol - 1) * gap) // 2
    y0 = 520
    zielone = int(ok * min(1.0, max(0.0, (t - 0.9) / 0.6)))
    for i in range(n):
        pa = pop(t, 0.02 + (i // kol) * 0.06, 0.25)
        if pa <= 0:
            continue
        x = x0 + (i % kol) * (s + gap)
        y = y0 + (i // kol) * (s + gap)
        kolor = ZIELONY if i < zielone else (90, 40, 46)
        sc = s * pa
        d.rounded_rectangle([x + (s - sc) / 2, y + (s - sc) / 2, x + (s + sc) / 2, y + (s + sc) / 2], radius=12,
                            fill=kolor + (255,))
    fb = f_anton(90)
    tl = p["tytul"]
    d.text((CX - szer(d, tl, fb) // 2, 330), tl, font=fb, fill=BIEL + (255,))
    yk = y0 + ((n - 1) // kol + 1) * (s + gap) + 20
    pl = wej(t, 0.9, 0.4)
    for j, (kolor, tekst) in enumerate([(ZIELONY, p["leg_ok"]), ((90, 40, 46), p["leg_zle"])]):
        yy = yk + j * 60
        d.rounded_rectangle([X0 + 60, yy, X0 + 100, yy + 40], radius=8, fill=kolor + (int(255 * pl),))
        d.text((X0 + 120, yy), tekst, font=f_inter(34), fill=BIEL + (int(255 * pl),))
    im.alpha_composite(nak)


def scena_dwa_banery(im, t, dl, p, kt):
    """Dwa banery: z odmowa i bez. Pod tym bez odmowy licznik zgod rosnie o +22."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.35)
    w = 380
    lx0, rx0 = X0, X1 - w
    y = 680
    d.text((lx0, y - 70), "z przyciskiem odmowy", font=f_inter(28), fill=SZARY + (int(255 * a),))
    d.text((rx0, y - 70), "bez odmowy", font=f_inter(28), fill=SZARY + (int(255 * a),))
    baner(d, lx0, y, lx0 + w, a, odmowa=True, skala=w / 520, akc=akc)
    pb = wej(t, 0.4, 0.35)
    baner(d, rx0, y, rx0 + w, pb, odmowa=False, skala=w / 520, akc=akc)
    pz = pop(t, 1.0, 0.45)
    if pz > 0:
        fb = f_anton(150 * pz)
        tl = p["wynik"]
        d.text((rx0 + w / 2 - szer(d, tl, fb) / 2, y + 300), tl, font=fb, fill=ZIELONY + (255,))
        fl = f_inter(34)
        d.text((rx0 + w / 2 - szer(d, p["podpis"], fl) / 2, y + 480), p["podpis"], font=fl, fill=BIEL + (255,))
    im.alpha_composite(nak)


def scena_ustawienia(im, t, dl, p, kt):
    """Wniosek: klik w 'ustawienia' otwiera drugi ekran z 'Odrzuc wszystkie'."""
    akc = kt["akcent"]
    nak, d = warstwa()
    x0, x1 = CX - 300, CX + 300
    y = 520
    t_klik = 0.7
    if t < t_klik + 0.2:
        h, us = baner(d, x0, y, x1, wej(t, 0, 0.3), skala=600 / 520, akc=akc)
        pk = wej(t, 0.2, 0.45)
        fx, fy = us[0] + 160 * (1 - pk), us[1] + 160 * (1 - pk)
        d.ellipse([fx - 28, fy - 28, fx + 28, fy + 28], outline=BIEL + (230,), width=6)
    else:
        a = wej(t, t_klik + 0.2, 0.3)
        d.rounded_rectangle([x0, y, x1, y + 520], radius=26, fill=(250, 250, 248, int(255 * a)))
        d.text((x0 + 30, y + 26), "Ustawienia prywatności", font=f_inter(32), fill=(30, 30, 34, int(255 * a)))
        for i in range(3):
            yy = y + 100 + i * 70
            d.rounded_rectangle([x0 + 30, yy + 10, x1 - 150, yy + 30], radius=8, fill=(190, 190, 196, int(255 * a)))
            d.rounded_rectangle([x1 - 110, yy, x1 - 40, yy + 40], radius=20, fill=(200, 200, 206, int(255 * a)))
            d.ellipse([x1 - 106, yy + 4, x1 - 74, yy + 36], fill=BIEL + (int(255 * a),))
        pz = pop(t, t_klik + 0.6, 0.4)
        sc = max(pz, 0.001)
        by = y + 360
        d.rounded_rectangle([x0 + 30, by, x1 - 30, by + 110], radius=20, fill=ZIELONY + (int(255 * a),))
        tl = "Odrzuć wszystkie"
        fb = f_inter(40)
        d.text((CX - szer(d, tl, fb) // 2, by + 30), tl, font=fb, fill=BIEL + (int(255 * a),))
        if pz > 0:
            d.rounded_rectangle([x0 + 20, by - 10, x1 - 20, by + 120], radius=24, outline=ZIELONY + (int(160 * pz),), width=6)
    im.alpha_composite(nak)



# ============================================================= przycisk na przejsciu (13.11)

def ludzik(d, cx, cy, r, kol, a, idzie=False):
    """Piktogram z sygnalizatora: stoi albo idzie."""
    k = kol + (int(255 * a),)
    w = max(4, int(r * 0.16))
    d.ellipse([cx - r * 0.2, cy - r, cx + r * 0.2, cy - r * 0.6], fill=k)
    if idzie:
        d.line([cx, cy - r * 0.55, cx - r * 0.05, cy + r * 0.15], fill=k, width=int(w * 1.5))
        d.line([cx - r * 0.05, cy + r * 0.15, cx - r * 0.38, cy + r * 0.85], fill=k, width=w)
        d.line([cx - r * 0.05, cy + r * 0.15, cx + r * 0.32, cy + r * 0.85], fill=k, width=w)
        d.line([cx, cy - r * 0.45, cx - r * 0.38, cy - r * 0.02], fill=k, width=w)
        d.line([cx, cy - r * 0.45, cx + r * 0.38, cy - r * 0.08], fill=k, width=w)
    else:
        d.line([cx, cy - r * 0.55, cx, cy + r * 0.15], fill=k, width=int(w * 1.8))
        d.line([cx - r * 0.08, cy + r * 0.15, cx - r * 0.12, cy + r * 0.85], fill=k, width=w)
        d.line([cx + r * 0.08, cy + r * 0.15, cx + r * 0.12, cy + r * 0.85], fill=k, width=w)
        d.line([cx - r * 0.14, cy - r * 0.5, cx - r * 0.24, cy + r * 0.1], fill=k, width=w)
        d.line([cx + r * 0.14, cy - r * 0.5, cx + r * 0.24, cy + r * 0.1], fill=k, width=w)


def sygnalizator(d, cx, cy, s, zielone, a):
    """Sygnalizator dla pieszych: u gory czerwony ludzik, na dole zielony; zielone 0..1."""
    w, h = 200 * s, 400 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(26 * s),
                        fill=(28, 28, 32, int(255 * a)), outline=(80, 80, 88, int(255 * a)), width=4)
    r = 78 * s
    for i, (kol, on, idzie) in enumerate([(CZERW, 1 - zielone, False), (ZIELONY, zielone, True)]):
        ly = cy - h / 4 + i * h / 2
        d.ellipse([cx - r, ly - r, cx + r, ly + r], fill=(14, 14, 16, int(255 * a)))
        kk = tuple(int(45 + (c - 45) * (0.15 + 0.85 * on)) for c in kol)
        ludzik(d, cx, ly, r * 0.8, kk, a, idzie)
    return cx, cy + h / 2


def skrzynka(d, cx, cy, s, a, wcisk=0.0, czekaj=0.0):
    """Zolta skrzynka z przyciskiem; wcisk 0..1 wgniata przycisk, czekaj zapala lampke."""
    w, h = 240 * s, 320 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(30 * s),
                        fill=(246, 196, 48, int(255 * a)))
    f = f_inter(max(14, int(30 * s)))
    tl = "WCIŚNIJ"
    d.text((cx - szer(d, tl, f) / 2, cy - h / 2 + 24 * s), tl, font=f, fill=(30, 26, 20, int(255 * a)))
    by = cy + 20 * s
    d.ellipse([cx - 78 * s, by - 78 * s, cx + 78 * s, by + 78 * s], fill=(40, 38, 40, int(255 * a)))
    r = 62 * s * (1 - 0.14 * wcisk)
    jas = int(236 - 50 * wcisk)
    d.ellipse([cx - r, by - r, cx + r, by + r], fill=(jas, jas, jas + 4, int(255 * a)))
    lk = tuple(int(70 + (c - 70) * czekaj) for c in ZOLTY)
    d.rounded_rectangle([cx - 60 * s, cy + h / 2 - 40 * s, cx + 60 * s, cy + h / 2 - 20 * s], radius=8,
                        fill=lk + (int(255 * a),))
    return cx, by


def wcisk_fazy(t, start, okres):
    """0..1..0 co `okres` sekund od `start` - palec wciska przycisk."""
    if t < start:
        return 0.0
    q = ((t - start) % okres) / okres
    return max(0.0, math.sin(math.pi * min(1.0, q / 0.45)))


def palec(d, x, y, a, wcisk):
    rr = 34 - 8 * wcisk
    d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 255, 255, int(235 * a)), width=7)
    if wcisk > 0.6:
        q = (wcisk - 0.6) / 0.4
        r2 = 50 + 40 * q
        d.ellipse([x - r2, y - r2, x + r2, y + r2], outline=ZOLTY + (int(200 * (1 - q) * a),), width=5)


def smuga(im, t, od=0.15, do=0.95):
    """Smuga swiatla przez caly kadr - ruch od pierwszej chwili."""
    if not od < t < do:
        return
    ps = (t - od) / (do - od)
    nak, d = warstwa()
    sx = int(-W * 0.7 + ps * W * 2.3)
    moc = int(150 * math.sin(math.pi * ps))
    for kk in range(6):
        d.line([sx + kk * 46, H, sx + kk * 46 + 700, 0], fill=(255, 255, 255, max(0, moc - kk * 18)), width=46)
    im.alpha_composite(nak.filter(ImageFilter.GaussianBlur(22)))


def ik_zegar(d, cx, cy, r, kol, a, t):
    k = kol + (int(255 * a),)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 24, 28, int(255 * a)), outline=k, width=max(5, int(r * 0.1)))
    for i in range(12):
        an = i * math.pi / 6
        d.line([cx + r * 0.78 * math.cos(an), cy + r * 0.78 * math.sin(an),
                cx + r * 0.9 * math.cos(an), cy + r * 0.9 * math.sin(an)], fill=k, width=4)
    an = t * 2 * math.pi / 2.4 - math.pi / 2
    d.line([cx, cy, cx + r * 0.7 * math.cos(an), cy + r * 0.7 * math.sin(an)], fill=k, width=max(4, int(r * 0.08)))
    an2 = t * 2 * math.pi / 28.8 - math.pi / 2
    d.line([cx, cy, cx + r * 0.45 * math.cos(an2), cy + r * 0.45 * math.sin(an2)], fill=k, width=max(5, int(r * 0.11)))
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=k)


def cykl_zegara(t, okres=2.4):
    """Swiatlo z zegara: pol okresu czerwone, pol zielone, miekkie przejscie."""
    q = (t % okres) / okres
    return min(1.0, max(0.0, (math.sin(2 * math.pi * q - math.pi / 2) + 0.2) * 3))


def scena_pytanie_przycisk(im, t, dl, p, kt):
    """Pytanie + slup z sygnalizatorem i zolta skrzynka; palec wciska przycisk raz za razem."""
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, kt["akcent"])
    nak, d = warstwa()
    y0 = dol + 60
    d.rounded_rectangle([CX - 18, y0, CX + 18, 1360], radius=10, fill=(96, 98, 106, 255))
    sygnalizator(d, CX - 150, y0 + 230, 1.05, 0.0, 1.0)
    bx, by = skrzynka(d, CX + 150, y0 + 560, 0.95, 1.0, wcisk_fazy(t, 0.1, 0.6), 0.5 + 0.5 * math.sin(t * 5))
    palec(d, bx + 6, by + 6, wej(t, 0.0, 0.1), wcisk_fazy(t, 0.1, 0.6))
    im.alpha_composite(nak)
    smuga(im, t)


def scena_wzywa(im, t, dl, p, kt):
    """Jak myslimy: przycisk wysyla sygnal do swiatel, a te zmieniaja sie na zielone."""
    nak, d = warstwa()
    a = wej(t, 0, 0.35)
    fb = f_anton(80)
    tl = p.get("tytul", "TAK MYŚLIMY")
    d.text((CX - szer(d, tl, fb) // 2, 330), tl, font=fb, fill=BIEL + (int(255 * a),))
    bx, by = skrzynka(d, CX - 190, 900, 0.95, a, wcisk_fazy(t, 0.15, 10), wej(t, 0.3, 0.2))
    palec(d, bx + 6, by + 6, a * (1 - wej(t, 0.6, 0.3)), wcisk_fazy(t, 0.15, 10))
    ps = wej(t, 0.35, 0.6)
    if ps > 0:
        strzalka(d, (CX - 50, 860), (CX + 70, 760), ZOLTY, a, grub=10, postep=ps, kreska=True, t=t)
    sygnalizator(d, CX + 200, 760, 1.0, wej(t, 1.0, 0.3), a)
    im.alpha_composite(nak)


def scena_przyciski_nyc(im, t, dl, p, kt):
    """65 kafelkow = 3250 przyciskow (1 kafelek = 50). Na slowie p['gasnie'] 50 kafelkow gasnie i
    dostaje krzyzyk (bez wplywu na swiatla), 15 zostaje zoltych (dzialaly)."""
    nak, d = warstwa()
    n, zle, na = p["n"], p["zle"], p["na_kafelek"]
    kol, s, gap = 10, 62, 12
    x0 = CX - (kol * s + (kol - 1) * gap) // 2
    y0 = 540
    try:
        tg = kt["czas_slowa"](p["gasnie"]) - kt["od"]
    except SystemExit:
        tg = 1.2
    fb = f_anton(90)
    tl = p["tytul"]
    d.text((CX - szer(d, tl, fb) // 2, 300), tl, font=fb, fill=BIEL + (int(255 * wej(t, 0, 0.3)),))
    fp = f_inter(34, False)
    d.text((CX - szer(d, p["podtytul"], fp) // 2, 420), p["podtytul"], font=fp, fill=SZARY + (int(255 * wej(t, 0.1, 0.3)),))
    for i in range(n):
        pa = pop(t, 0.05 + (i // kol) * 0.06, 0.25)
        if pa <= 0:
            continue
        x = x0 + (i % kol) * (s + gap)
        y = y0 + (i // kol) * (s + gap)
        g = wej(t, tg + (i % zle if i < zle else 0) * 0.012, 0.25) if i < zle else 0.0
        kolor = mieszaj((246, 196, 48), (66, 60, 62), g)
        sc = s * pa
        d.rounded_rectangle([x + (s - sc) / 2, y + (s - sc) / 2, x + (s + sc) / 2, y + (s + sc) / 2], radius=12,
                            fill=tuple(int(c) for c in kolor) + (255,))
        if g > 0.5:
            m = 18
            d.line([x + m, y + m, x + s - m, y + s - m], fill=CZERW + (int(255 * (g - 0.5) * 2),), width=6)
            d.line([x + s - m, y + m, x + m, y + s - m], fill=CZERW + (int(255 * (g - 0.5) * 2),), width=6)
    yk = y0 + ((n - 1) // kol + 1) * (s + gap) + 24
    pl = wej(t, tg + 0.4, 0.4)
    for j, (kolor, tekst) in enumerate([((66, 60, 62), p["leg_zle"]), ((246, 196, 48), p["leg_ok"])]):
        yy = yk + j * 62
        d.rounded_rectangle([X0 + 60, yy, X0 + 100, yy + 40], radius=8, fill=kolor + (int(255 * pl),))
        d.text((X0 + 120, yy), tekst, font=dopasuj(d, tekst, X1 - X0 - 140, 34, 26), fill=BIEL + (int(255 * pl),))
    fk = f_inter(26, False)
    d.text((X0 + 60, yk + 140), f"1 kwadrat = {na} przycisków", font=fk, fill=SZARY + (int(255 * pl),))
    im.alpha_composite(nak)


def scena_zegar(im, t, dl, p, kt):
    """Mechanizm: kabel od przycisku przeciety, swiatla przelacza zegar."""
    nak, d = warstwa()
    a = wej(t, 0, 0.35)
    sx, sy = CX, 640
    # zegar przestawia swiatlo na zielone sam, bez przycisku (scena trwa ~1,3 s)
    dol_s = sygnalizator(d, sx, sy, 0.95, wej(t, 0.7, 0.25), a)
    bx, by = CX - 230, 1090
    cx, cy = CX + 230, 1090
    # kabel od przycisku - przekreslony
    d.line([bx, by - 150, sx - 40, dol_s[1]], fill=(110, 110, 118, int(255 * a)), width=8)
    krzyzyk(d, (bx + sx - 40) / 2, (by - 150 + dol_s[1]) / 2, 34, a, wej(t, 0.2, 0.4))
    # kabel od zegara - zywy
    pz = wej(t, 0.35, 0.4)
    strzalka(d, (cx, by - 112), (sx + 40, dol_s[1] + 6), ZIELONY, a * pz, grub=9, postep=max(0.01, pz), kreska=True, t=t)
    skrzynka(d, bx, by, 0.8, a, 0.0, 0.0)
    ik_zegar(d, cx, cy, 100 * max(0.01, pop(t, 0.3, 0.4)), BIEL, a, t)
    f = f_inter(32)
    for x, tx, kol in [(bx, "przycisk", SZARY), (cx, "zegar", ZIELONY)]:
        d.text((x - szer(d, tx, f) / 2, 1250), tx, font=f, fill=kol + (int(255 * a),))
    im.alpha_composite(nak)


def scena_dziesiec(im, t, dl, p, kt):
    """Wniosek: 10 wcisniec - licznik rosnie, a zegar i swiatla ida swoim tempem."""
    nak, d = warstwa()
    a = wej(t, 0, 0.35)
    okres = 0.16
    ile = min(10, int(max(0.0, t - 0.15) / okres) + (1 if t > 0.15 else 0))
    wc = wcisk_fazy(t, 0.15, okres) if ile < 10 else 0.0
    bx, by = skrzynka(d, CX - 190, 900, 0.95, a, wc, 1.0)
    palec(d, bx + 6, by + 6, a, wc)
    fb = f_anton(150)
    tl = f"{ile}×"
    d.text((bx - szer(d, tl, fb) / 2, 480), tl, font=fb, fill=ZOLTY + (int(255 * a),))
    sygnalizator(d, CX + 200, 800, 0.95, 0.0, a)
    ik_zegar(d, CX + 200, 1120, 70, BIEL, a, t)
    if ile >= 10:
        pz = pop(t, 0.15 + 10 * okres + 0.2, 0.4)
        if pz > 0:
            f = f_anton(int(60 * pz) + 1)
            tx = p.get("puenta", "ZIELONE I TAK PRZYJDZIE")
            f = dopasuj(d, tx, X1 - X0, int(60 * pz) + 1, 30, f_anton)
            d.text((CX - szer(d, tx, f) / 2, 1250), tx, font=f, fill=ZIELONY + (255,))
    im.alpha_composite(nak)


SCENY_PRZYCISK = {"pytanie_przycisk": scena_pytanie_przycisk, "wzywa": scena_wzywa,
                  "przyciski_nyc": scena_przyciski_nyc, "zegar": scena_zegar, "dziesiec": scena_dziesiec}


# ============================================================= 14.11: bateria, sasiedni pas, "nie jestem robotem"

def ptaszek(d, cx, cy, r, a=1.0, kol=ZIELONY):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=kol + (int(255 * a),))
    d.line([cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.38, cx + r * 0.5, cy - r * 0.35],
           fill=BIEL + (int(255 * a),), width=max(6, int(r * 0.18)), joint="curve")


def linie_tekstu(d, linie, cx, y, a, kol=BIEL, px=64, maks_w=None):
    for l in linie:
        f = dopasuj(d, l, maks_w or (X1 - X0), px, 30, f_anton)
        d.text((cx - szer(d, l, f) // 2, y), l, font=f, fill=kol + (int(255 * a),))
        y += f.size + 10
    return y


def bateria_ik(d, cx, cy, w, h, poziom, a, kol=ZIELONY, piorun=False, napis=True):
    """Pionowa bateria; poziom 0..1."""
    g = max(6, int(w * 0.06))
    d.rounded_rectangle([cx - w * 0.2, cy - h / 2 - h * 0.06, cx + w * 0.2, cy - h / 2 + 4], radius=8,
                        fill=(200, 200, 206, int(255 * a)))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(w * 0.16),
                        outline=(220, 220, 226, int(255 * a)), width=g)
    m = g + 8
    wys = (h - 2 * m) * max(0.0, min(1.0, poziom))
    if wys > 4:
        d.rounded_rectangle([cx - w / 2 + m, cy + h / 2 - m - wys, cx + w / 2 - m, cy + h / 2 - m],
                            radius=int(w * 0.08), fill=kol + (int(255 * a),))
    if napis:
        tl = f"{int(round(poziom * 100))}%"
        f = f_anton(int(w * 0.36))
        d.text((cx - szer(d, tl, f) / 2, cy - f.size * 0.62), tl, font=f, fill=BIEL + (int(255 * a),))
    if piorun:
        s = w * 0.22
        y = cy + h * 0.28
        d.polygon([(cx + s * 0.1, y - s), (cx - s * 0.5, y + s * 0.1), (cx - s * 0.05, y + s * 0.1),
                   (cx - s * 0.15, y + s), (cx + s * 0.5, y - s * 0.15), (cx + s * 0.05, y - s * 0.15)],
                  fill=ZOLTY + (int(255 * a),))


def ksiezyc(d, cx, cy, r, a, kol=(236, 232, 210)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=kol + (int(255 * a),))
    d.ellipse([cx - r + r * 0.55, cy - r - r * 0.2, cx + r + r * 0.55, cy + r - r * 0.2], fill=(0, 0, 0, 0))


def ksiezyc_na(im, cx, cy, r, a):
    """Sierp: rysowany na osobnej warstwie, zeby 'wyciecie' bylo przezroczyste."""
    nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(nak)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(236, 232, 210, int(255 * a)))
    d.ellipse([cx - r + r * 0.6, cy - r - r * 0.25, cx + r + r * 0.6, cy + r - r * 0.25], fill=(0, 0, 0, 0))
    im.alpha_composite(nak)


def budzik(d, cx, cy, r, a, kol=BIEL):
    k = kol + (int(255 * a),)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=k, width=max(4, int(r * 0.14)))
    d.ellipse([cx - r * 1.05, cy - r * 1.25, cx - r * 0.45, cy - r * 0.7], fill=k)
    d.ellipse([cx + r * 0.45, cy - r * 1.25, cx + r * 1.05, cy - r * 0.7], fill=k)
    d.line([cx, cy, cx, cy - r * 0.55], fill=k, width=max(3, int(r * 0.12)))
    d.line([cx, cy, cx + r * 0.4, cy + r * 0.2], fill=k, width=max(3, int(r * 0.12)))


def scena_pytanie_bateria(im, t, dl, p, kt):
    """Pytanie + telefon na kablu w nocy; bateria laduje sie na ekranie."""
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, kt["akcent"])
    nak, d = warstwa()
    cy = dol + 460
    d.line([CX, cy + 340, CX, 1400], fill=(200, 200, 206, 255), width=12)
    im.alpha_composite(nak)

    def ekran(im2, box, tt, a):
        x0, y0, x1, y1 = box
        n2, d2 = warstwa()
        d2.rounded_rectangle(box, radius=40, fill=(22, 24, 36, int(255 * a)))
        bcx = (x0 + x1) // 2
        poz = 0.55 + 0.45 * min(1.0, tt / 2.6)
        bateria_ik(d2, bcx, (y0 + y1) // 2 + 40, 170, 300, poz, a, piorun=True)
        f = f_inter(30, False)
        tx = "02:47"
        d2.text((bcx - szer(d2, tx, f) / 2, y0 + 70), tx, font=f, fill=(200, 200, 210, int(255 * a)))
        im2.alpha_composite(n2)
        ksiezyc_na(im2, bcx + 90, y0 + 150, 34, a)
    telefon(im, CX, cy, 0.9, 1.0, ekran, t)
    smuga(im, t)


def scena_zuzycie(im, t, dl, p, kt):
    """Bateria stoi na 100%, a od niej rozchodza sie czerwone fale zuzycia."""
    nak, d = warstwa()
    a = wej(t, 0, 0.35)
    cx, cy = CX, 820
    for k in range(3):
        q = ((t - 0.3 - k * 0.45) % 1.35) / 1.35 if t > 0.3 + k * 0.45 else -1
        if q >= 0:
            r = 200 + 260 * q
            d.ellipse([cx - r * 0.75, cy - r, cx + r * 0.75, cy + r], outline=CZERW + (int(200 * (1 - q) * a),), width=8)
    puls = 0.5 + 0.5 * math.sin(t * 5)
    kol = mieszaj(ZIELONY, (240, 140, 60), wej(t, 0.4, 0.8) * (0.6 + 0.4 * puls))
    bateria_ik(d, cx, cy, 280, 520, 1.0, a, kol=kol)
    f = dopasuj(d, p["podpis"], X1 - X0, 40, 28)
    d.text((CX - szer(d, p["podpis"], f) / 2, 1200), p["podpis"], font=f, fill=BIEL + (int(255 * wej(t, 0.5, 0.4)),))
    im.alpha_composite(nak)


def scena_noce(im, t, dl, p, kt):
    """7 nocy - telefon zapamietuje, o ktorej co dzien wstajesz."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    fb = f_anton(80)
    tl = p.get("tytul", "UCZY SIĘ")
    d.text((CX - szer(d, tl, fb) / 2, 330), tl, font=fb, fill=BIEL + (int(255 * a),))
    dni = ["pn", "wt", "śr", "cz", "pt", "sb", "nd"]
    godz = p.get("godziny", ["6:30"] * 5 + ["9:00"] * 2)
    krok = 108
    x0 = CX - krok * 3
    for i, (dz, g) in enumerate(zip(dni, godz)):
        x = x0 + i * krok
        pa = wej(t, 0.05 + i * 0.05, 0.25)
        d.rounded_rectangle([x - 46, 560, x + 46, 960], radius=22, fill=(34, 36, 50, int(255 * pa)))
        f = f_inter(30)
        d.text((x - szer(d, dz, f) / 2, 580), dz, font=f, fill=SZARY + (int(255 * pa),))
        pz = pop(t, 0.45 + i * 0.16, 0.3)
        if pz > 0:
            budzik(d, x, 760, 30 * pz, 1.0, ZOLTY)
            fg = f_inter(26)
            d.text((x - szer(d, g, fg) / 2, 850), g, font=fg, fill=ZOLTY + (int(255 * min(1, pz)),))
    im.alpha_composite(nak)
    for i in range(7):
        pa = wej(t, 0.05 + i * 0.05, 0.25)
        ksiezyc_na(im, x0 + i * krok, 660, 22, pa)


def scena_wykres_80(im, t, dl, p, kt):
    """Ladowanie w nocy: rosnie do 80%, stoi, konczy tuz przed budzikiem."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    gx0, gx1, gy0, gy1 = X0 + 60, X1 - 40, 560, 1160
    d.line([gx0, gy1, gx1, gy1], fill=(120, 120, 130, int(255 * a)), width=4)
    def py(v):
        return gy1 - (gy1 - gy0) * v
    for v, tx in ((0.8, "80%"), (1.0, "100%")):
        y = py(v)
        for xx in range(gx0, gx1, 28):
            d.line([xx, y, xx + 14, y], fill=(90, 90, 100, int(200 * a)), width=3)
        f = f_inter(30)
        d.text((gx0 - 10 - szer(d, tx, f), y - 18), tx, font=f, fill=(SZARY if v == 1.0 else ZOLTY) + (int(255 * a),))
    pts = []
    for i in range(101):
        u = i / 100
        if u < 0.25:
            v = 0.2 + 0.6 * (u / 0.25)
        elif u < 0.8:
            v = 0.8
        elif u < 0.95:
            v = 0.8 + 0.2 * ((u - 0.8) / 0.15)
        else:
            v = 1.0
        pts.append((gx0 + (gx1 - gx0) * u, py(v)))
    pr = wej(t, 0.2, 1.6)
    n = max(2, int(len(pts) * pr))
    d.line(pts[:n], fill=ZIELONY + (255,), width=10, joint="curve")
    xe, ye = pts[n - 1]
    d.ellipse([xe - 14, ye - 14, xe + 14, ye + 14], fill=ZIELONY + (255,))
    f = f_inter(30)
    for tx, x in ((p.get("od_godz", "23:00"), gx0), (p.get("do_godz", "6:30"), gx1)):
        d.text((x - szer(d, tx, f) / 2, gy1 + 20), tx, font=f, fill=SZARY + (int(255 * a),))
    pb = pop(t, 1.5, 0.35)
    if pb > 0:
        budzik(d, gx1, gy0 - 70, 36 * pb, 1.0, ZOLTY)
    if pr > 0.5:
        fs = f_inter(30, False)
        tx = "czeka"
        xm = gx0 + (gx1 - gx0) * 0.52
        d.text((xm - szer(d, tx, fs) / 2, py(0.8) - 54), tx, font=fs, fill=ZOLTY + (int(255 * wej(t, 0.9, 0.3)),))
    im.alpha_composite(nak)


def scena_wniosek_ok(im, t, dl, p, kt):
    """Wniosek: duzy zielony ptaszek i jedno haslo."""
    nak, d = warstwa()
    pz = pop(t, 0.1, 0.45)
    if pz > 0:
        ptaszek(d, CX, 700, 150 * pz)
        linie_tekstu(d, p["linie"], CX, 920, min(1.0, pz), px=80)
    im.alpha_composite(nak)


# ---------- sasiedni pas

def auto(d, cx, cy, s, kol, a):
    """Auto z gory: karoseria, szyby, kola."""
    w, h = 92 * s, 160 * s
    ka = int(255 * a)
    for dx in (-1, 1):
        for dy in (-0.3, 0.3):
            d.rounded_rectangle([cx + dx * w * 0.52 - 9 * s, cy + dy * h - 18 * s, cx + dx * w * 0.52 + 9 * s, cy + dy * h + 18 * s],
                                radius=4, fill=(20, 20, 22, ka))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(26 * s), fill=kol + (ka,))
    d.rounded_rectangle([cx - w * 0.36, cy - h * 0.28, cx + w * 0.36, cy - h * 0.1], radius=int(8 * s), fill=(30, 34, 44, ka))
    d.rounded_rectangle([cx - w * 0.36, cy + h * 0.2, cx + w * 0.36, cy + h * 0.32], radius=int(8 * s), fill=(30, 34, 44, ka))


def droga(d, cx, y0, y1, a, przesun=0.0, pasy=2, szer_pasa=200):
    w = pasy * szer_pasa
    d.rectangle([cx - w / 2, y0, cx + w / 2, y1], fill=(44, 44, 50, int(255 * a)))
    for k in (-1, 1):
        d.line([cx + k * w / 2, y0, cx + k * w / 2, y1], fill=(220, 220, 226, int(255 * a)), width=6)
    for i in range(1, pasy):
        x = cx - w / 2 + i * szer_pasa
        y = y0 - 80 + (przesun % 80)
        while y < y1:
            yy0, yy1 = max(y, y0), min(y + 44, y1)
            if yy1 > yy0:
                d.line([x, yy0, x, yy1], fill=(230, 230, 230, int(220 * a)), width=6)
            y += 80


def kolumna_aut(d, x, y0, y1, przes, odst, a, kol=(150, 152, 162), znikaj_ponizej=None):
    y = y0 - odst + (przes % odst)
    while y < y1 + odst:
        if y0 + 60 < y < y1 - 60:
            aa = a
            if znikaj_ponizej is not None and y > znikaj_ponizej:
                aa = a * max(0.0, 1 - (y - znikaj_ponizej) / 160)
            auto(d, x, y, 1.0, kol, aa)
        y += odst


def scena_pytanie_pas(im, t, dl, p, kt):
    """Pytanie + korek z gory: ty stoisz, sasiedni pas sie toczy."""
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, kt["akcent"])
    nak, d = warstwa()
    y0, y1 = dol + 40, 1380
    droga(d, CX, y0, y1, 1.0)
    kolumna_aut(d, CX + 100, y0, y1, -t * 140, 250, 1.0)
    for y in (y0 + 160, y0 + 600):
        auto(d, CX - 100, y, 1.0, (150, 152, 162), 1.0)
    auto(d, CX - 100, y0 + 380, 1.0, ZOLTY, 1.0)
    im.alpha_composite(nak)
    smuga(im, t)


def scena_mijaja(im, t, dl, p, kt):
    """Stoisz: auta obok mijaja cie powoli, kazde dlugo na widoku."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    fb = f_anton(80)
    tl = p.get("tytul", "STOISZ")
    d.text((CX - szer(d, tl, fb) / 2, 300), tl, font=fb, fill=BIEL + (int(255 * a),))
    y0, y1 = 430, 1360
    droga(d, CX, y0, y1, a)
    kolumna_aut(d, CX + 100, y0, y1, -t * 90, 240, a)
    auto(d, CX - 100, 900, 1.0, ZOLTY, a)
    im.alpha_composite(nak)


def scena_wyprzedzasz(im, t, dl, p, kt):
    """Jedziesz: mijasz auta w sekunde, a minietych od razu nie pamietasz (znikaja)."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    fb = f_anton(80)
    tl = p.get("tytul", "JEDZIESZ")
    d.text((CX - szer(d, tl, fb) / 2, 300), tl, font=fb, fill=BIEL + (int(255 * a),))
    y0, y1 = 430, 1360
    droga(d, CX, y0, y1, a, przesun=t * 700)
    kolumna_aut(d, CX + 100, y0, y1, t * 520, 260, a, znikaj_ponizej=960)
    auto(d, CX - 100, 900, 1.0, ZOLTY, a)
    im.alpha_composite(nak)


def scena_meta(im, t, dl, p, kt):
    """Dwa auta: jedno trzyma pas, drugie zmienia pasy - na mete wjezdzaja razem."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    y0, y1, meta = 560, 1320, 640
    f = f_inter(30)
    for cx, tx in ((CX - 200, p.get("lewy", "bez zmiany")), (CX + 200, p.get("prawy", "zmiana pasa"))):
        droga(d, cx, y0, y1, a, szer_pasa=140)
        d.text((cx - szer(d, tx, f) / 2, y0 - 60), tx, font=f, fill=SZARY + (int(255 * a),))
    for i in range(10):
        kk = (240, 240, 240) if i % 2 == 0 else (30, 30, 34)
        d.rectangle([CX - 340 + i * 28, meta - 10, CX - 340 + (i + 1) * 28, meta + 10], fill=kk + (int(255 * a),))
        d.rectangle([CX + 60 + i * 28, meta - 10, CX + 60 + (i + 1) * 28, meta + 10], fill=kk + (int(255 * a),))
    pr = wej(t, 0.2, 1.5)
    y = 1220 - (1220 - meta - 90) * pr
    auto(d, CX - 200 - 70, y, 0.8, ZOLTY, a)
    zyg = math.sin(pr * math.pi * 3)
    auto(d, CX + 200 + 70 * (1 if zyg > 0 else -1) * min(1, abs(zyg) * 2), y, 0.8, ZOLTY, a)
    pz = pop(t, 1.8, 0.4)
    if pz > 0:
        tx = p.get("puenta", "TEN SAM CZAS")
        fb = f_anton(max(1, int(76 * pz)))
        d.text((CX - szer(d, tx, fb) / 2, 400), tx, font=fb, fill=ZIELONY + (255,))
    im.alpha_composite(nak)


# ---------- "nie jestem robotem"

def kursor(d, x, y, s, a):
    pts = [(0, 0), (0, 46), (12, 35), (21, 56), (30, 52), (21, 32), (38, 32)]
    d.polygon([(x + px * s, y + py * s) for px, py in pts], fill=BIEL + (int(255 * a),), outline=(20, 20, 20, int(255 * a)))


def widget_robot(d, x0, y0, x1, a, stan=0.0, t=0.0):
    """Okienko 'Nie jestem robotem'; stan: 0 puste, 0..1 krecioleczek, 1 ptaszek."""
    h = 150
    ka = int(255 * a)
    d.rounded_rectangle([x0, y0, x1, y0 + h], radius=14, fill=(249, 249, 249, ka), outline=(210, 210, 214, ka), width=3)
    bx, by, bs = x0 + 34, y0 + 45, 60
    if stan <= 0:
        d.rounded_rectangle([bx, by, bx + bs, by + bs], radius=6, fill=(255, 255, 255, ka), outline=(150, 150, 156, ka), width=4)
    elif stan < 1:
        st = t * 540
        d.arc([bx, by, bx + bs, by + bs], st, st + 270, fill=(66, 133, 244, ka), width=7)
    else:
        d.line([bx + 6, by + 32, bx + 24, by + 52, bx + 58, by + 6], fill=(30, 160, 70, ka), width=10, joint="curve")
    f = f_inter(34, False)
    d.text((bx + bs + 28, y0 + 52), "Nie jestem robotem", font=f, fill=(40, 40, 44, ka))
    return (bx + bs / 2, by + bs / 2)


def robot_ik(d, cx, cy, r, kol, a):
    k = kol + (int(255 * a),)
    d.line([cx, cy - r * 1.05, cx, cy - r * 0.7], fill=k, width=max(4, int(r * 0.08)))
    d.ellipse([cx - r * 0.12, cy - r * 1.22, cx + r * 0.12, cy - r * 0.98], fill=k)
    d.rounded_rectangle([cx - r * 0.8, cy - r * 0.7, cx + r * 0.8, cy + r * 0.6], radius=int(r * 0.25), fill=k)
    for dx in (-0.35, 0.35):
        d.ellipse([cx + dx * r - r * 0.14, cy - r * 0.25, cx + dx * r + r * 0.14, cy + r * 0.03], fill=(20, 20, 26, int(255 * a)))
    d.rounded_rectangle([cx - r * 0.35, cy + r * 0.22, cx + r * 0.35, cy + r * 0.34], radius=4, fill=(20, 20, 26, int(255 * a)))


def sciezka_kursora(t0, t1, t, start, cel, fala=60):
    q = max(0.0, min(1.0, (t - t0) / (t1 - t0)))
    q = 1 - (1 - q) ** 2
    x = start[0] + (cel[0] - start[0]) * q
    y = start[1] + (cel[1] - start[1]) * q + fala * math.sin(q * math.pi * 2) * (1 - q)
    return x, y, q


def scena_pytanie_captcha(im, t, dl, p, kt):
    """Pytanie + okno strony z 'Nie jestem robotem'; kursor dojezdza falista droga i klika."""
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, kt["akcent"])
    nak, d = warstwa()
    x0, y0, x1, y1 = X0 + 10, dol + 80, X1 - 10, dol + 700
    okno_przegladarki(d, x0, y0, x1, y1, 1.0, ciemne=False)
    for i in range(3):
        d.rounded_rectangle([x0 + 40, y0 + 110 + i * 46, x1 - 40 - i * 90, y0 + 132 + i * 46], radius=8, fill=(214, 214, 220, 255))
    stan = 0.0 if t < 1.3 else (0.5 if t < 1.8 else 1.0)
    cel = widget_robot(d, x0 + 40, y0 + 330, x1 - 40, 1.0, stan, t)
    slad = []
    for k in range(0, 40):
        tt = 0.1 + k * 0.03
        if tt > t:
            break
        xx, yy, _ = sciezka_kursora(0.1, 1.25, tt, (x1 - 60, y1 - 40), cel)
        slad.append((xx, yy))
    if len(slad) > 1:
        d.line(slad, fill=kt["akcent"] + (160,), width=5, joint="curve")
    xx, yy, q = sciezka_kursora(0.1, 1.25, t, (x1 - 60, y1 - 40), cel)
    kursor(d, xx, yy, 1.2, 1.0)
    if 1.25 < t < 1.6:
        r = 20 + 80 * (t - 1.25) / 0.35
        d.ellipse([cel[0] - r, cel[1] - r, cel[0] + r, cel[1] + r], outline=kt["akcent"] + (int(220 * (1.6 - t) / 0.35),), width=6)
    im.alpha_composite(nak)
    smuga(im, t)


def scena_litery(im, t, dl, p, kt):
    """Krzywe litery do przepisania; na slowie p['program'] wchodzi robot i odczytuje je: 99,8%."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    try:
        tp = kt["czas_slowa"](p["program"]) - kt["od"]
    except SystemExit:
        tp = 1.0
    bx0, by0, bx1, by1 = X0 + 40, 420, X1 - 40, 700
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=20, fill=(236, 234, 228, int(255 * a)))
    im.alpha_composite(nak)
    tekst = p.get("kod", "xK7mQ")
    for i, ch in enumerate(tekst):
        l = Image.new("RGBA", (160, 180), (0, 0, 0, 0))
        dl_ = ImageDraw.Draw(l)
        dl_.text((30, 10), ch, font=f_anton(130), fill=(40, 40, 46, int(255 * a)))
        l = l.rotate([-18, 14, -8, 20, -12][i % 5] + 4 * math.sin(t * 2 + i), resample=Image.BICUBIC)
        im.alpha_composite(l, (int(bx0 + 40 + i * 120), int(by0 + 40 + 18 * math.sin(i * 1.7))))
    nak, d = warstwa()
    pts = [(bx0 + 30 + k * 12, (by0 + by1) / 2 + 30 * math.sin(k * 0.3 + t)) for k in range(int((bx1 - bx0 - 60) / 12))]
    d.line(pts, fill=(40, 40, 46, int(200 * a)), width=5)
    pr = pop(t, tp, 0.4)
    if pr > 0:
        robot_ik(d, CX - 190, 960, 110 * pr, (170, 200, 230), 1.0)
        fb = f_anton(max(1, int(150 * pr)))
        tl = p.get("wynik", "99,8%")
        d.text((CX - 40, 870), tl, font=fb, fill=ZOLTY + (255,))
        fs = f_inter(32, False)
        d.text((CX - 30, 1060), p.get("podpis", "odczytanych przez program"), font=fs, fill=BIEL + (int(255 * min(1, pr)),))
    im.alpha_composite(nak)


def scena_zachowanie(im, t, dl, p, kt):
    """Liczy sie zachowanie: kursor kreci sie po stronie przed klikiem i po nim,
    a pasek 'czlowiek' rosnie z kazdym ruchem."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    cy = 760
    w0, w1 = CX - 240, CX + 240
    cel = widget_robot(d, w0, cy - 75, w1, a, 1.0 if t > 1.2 else 0.0, t)
    f = f_inter(34)
    for tx, x in (("przed", X0 + 20), ("po", X1 - 60)):
        d.text((x, cy - 180), tx, font=f, fill=SZARY + (int(255 * a),))
    pts = []
    for k in range(120):
        u = k / 119
        if u * 2.4 > t:
            break
        x = X0 + 40 + (X1 - X0 - 80) * u
        y = cy - 140 + 40 * math.sin(u * 17) + 20 * math.sin(u * 41)
        if 0.45 < u < 0.55:
            y = cy - 140 + (cel[1] - (cy - 140)) * math.sin((u - 0.45) / 0.1 * math.pi)
        pts.append((x, y))
    if len(pts) > 1:
        d.line(pts, fill=kt["akcent"] + (200,), width=5, joint="curve")
        kursor(d, pts[-1][0], pts[-1][1], 1.0, a)
    pk = min(1.0, t / 2.4)
    gx0, gx1, gy = X0 + 60, X1 - 60, 1080
    d.text((gx0, gy - 60), p.get("pasek", "człowiek?"), font=f_inter(32), fill=BIEL + (int(255 * a),))
    d.rounded_rectangle([gx0, gy, gx1, gy + 40], radius=20, fill=(50, 50, 58, int(255 * a)))
    d.rounded_rectangle([gx0, gy, gx0 + max(40, (gx1 - gx0) * 0.92 * pk), gy + 40], radius=20, fill=ZIELONY + (int(255 * a),))
    im.alpha_composite(nak)


def scena_zagadka(im, t, dl, p, kt):
    """Zagadka ze zdjeciami: siatka 3x3 z autami, nad nia znak zapytania 'system niepewny'."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    pz = pop(t, 0.1, 0.4)
    if pz > 0:
        r = 70 * pz
        d.ellipse([CX - r, 420 - r, CX + r, 420 + r], fill=ZOLTY + (255,))
        fq = f_anton(max(1, int(100 * pz)))
        d.text((CX - szer(d, "?", fq) / 2, 420 - fq.size * 0.62), "?", font=fq, fill=CIEMNY + (255,))
    x0, y0, s, g = CX - 270, 560, 170, 10
    d.rounded_rectangle([x0 - 16, y0 - 90, x0 + 3 * s + 2 * g + 16, y0 + 3 * s + 2 * g + 16], radius=16, fill=(249, 249, 249, int(255 * a)))
    d.rectangle([x0, y0 - 76, x0 + 3 * s + 2 * g, y0 - 10], fill=(66, 133, 244, int(255 * a)))
    ft = f_inter(30)
    d.text((x0 + 20, y0 - 64), p.get("zadanie", "Zaznacz wszystkie auta"), font=ft, fill=BIEL + (int(255 * a),))
    z_autem = {0, 4, 5, 7}
    for i in range(9):
        x, y = x0 + (i % 3) * (s + g), y0 + (i // 3) * (s + g)
        d.rectangle([x, y, x + s, y + s], fill=(120, 140, 120, int(255 * a)) if i % 2 else (110, 130, 150, int(255 * a)))
        if i in z_autem:
            auto(d, x + s / 2, y + s / 2, 0.75, (220, 70, 60), a)
        kl = list(sorted(z_autem)).index(i) if i in z_autem else -1
        if kl >= 0 and t > 0.9 + kl * 0.3:
            d.rectangle([x, y, x + s, y + s], outline=(66, 133, 244, 255), width=8)
            ptaszek(d, x + 26, y + 26, 20, 1.0, (66, 133, 244))
    im.alpha_composite(nak)


SCENY_1411 = {"pytanie_bateria": scena_pytanie_bateria, "zuzycie": scena_zuzycie, "noce": scena_noce,
              "wykres_80": scena_wykres_80, "wniosek_ok": scena_wniosek_ok,
              "pytanie_pas": scena_pytanie_pas, "mijaja": scena_mijaja, "wyprzedzasz": scena_wyprzedzasz, "meta": scena_meta,
              "pytanie_captcha": scena_pytanie_captcha, "litery": scena_litery, "zachowanie": scena_zachowanie,
              "zagadka": scena_zagadka}


# ============================================================= marketingowe (12.11 13:55: "tylko marketingowe ciekawostki")

def metka(d, cx, cy, w, h, linia1, linia2, kol, a, kat=0.0):
    """Metka cenowa z dziurka; tekst dwulinijkowy."""
    ka = int(255 * a)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=22, fill=kol + (ka,))
    d.ellipse([cx - 14, cy - h / 2 + 18, cx + 14, cy - h / 2 + 46], fill=(16, 16, 20, ka))
    # liczba i podpis w osobnych pasach: liczba w gornej czesci pod dziurka, podpis na dole -
    # pierwsza wersja nakladala dolna krawedz cyfr Anton na podpis
    f1 = dopasuj(d, linia1, w - 40, int(h * 0.3), 24, f_anton)
    bb = d.textbbox((0, 0), linia1, font=f1)
    y1 = cy - h * 0.2
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y1 - bb[1]), linia1, font=f1, fill=CIEMNY + (ka,))
    f2 = dopasuj(d, linia2, w - 40, int(h * 0.12), 18)
    bb2 = d.textbbox((0, 0), linia2, font=f2)
    y2 = max(y1 + (bb[3] - bb[1]) + h * 0.06, cy + h * 0.2)
    d.text((cx - (bb2[2] - bb2[0]) / 2 - bb2[0], y2 - bb2[1]), linia2, font=f2, fill=CIEMNY + (ka,))


def dwa_slupki(d, t, wart, etyk, kolory, y_dol=1150, wys_max=520, start=0.2, jedn="%"):
    """Dwa slupki rosnace od dolu; liczba nad slupkiem, etykieta pod nim (mierzona)."""
    szer_s = 220
    xs = [CX - 170, CX + 170]
    mx = max(wart)
    for i, (v, e, k) in enumerate(zip(wart, etyk, kolory)):
        p = wej(t, start + i * 0.25, 0.8)
        h = wys_max * v / mx * p
        x = xs[i]
        d.rounded_rectangle([x - szer_s / 2, y_dol - max(h, 6), x + szer_s / 2, y_dol], radius=18, fill=k + (255,))
        if p > 0.05:
            tl = f"{int(round(v * p))}{jedn}"
            fb = f_anton(96)
            d.text((x - szer(d, tl, fb) / 2, y_dol - h - 120), tl, font=fb, fill=BIEL + (255,))
        fe = dopasuj(d, e, 330, 36, 24)
        d.text((x - szer(d, e, fe) / 2, y_dol + 20), e, font=fe, fill=SZARY + (int(255 * wej(t, start, 0.3)),))


def scena_pytanie_dziennie(im, t, dl, p, kt):
    """Pytanie + dwie metki: '5 dziennie' i '150 miesiecznie' kolysza sie na sznurkach."""
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, kt["akcent"])
    for i, (l1, l2, kol) in enumerate([("5", "dziennie", ZIELONY), ("150", "miesięcznie", (240, 120, 100))]):
        nak = Image.new("RGBA", (420, 520), (0, 0, 0, 0))
        d = ImageDraw.Draw(nak)
        d.line([210, 0, 210, 120], fill=(200, 200, 206, 255), width=5)
        metka(d, 210, 300, 300, 330, l1, l2, kol, 1.0)
        kat = 7 * math.sin(t * 2.4 + i * 1.3) * (1 if t > 0.1 else 0)
        nak = nak.rotate(kat, center=(210, 0), resample=Image.BICUBIC)
        im.alpha_composite(nak, (int(CX - 210 + (-185 if i == 0 else 185)), int(dol + 60)))
    smuga(im, t)


def scena_ta_sama(im, t, dl, p, kt):
    """30 kratek kalendarza po 5 - sumuja sie w 150."""
    nak, d = warstwa()
    kol, s, g = 6, 100, 14
    x0 = CX - (kol * s + (kol - 1) * g) / 2
    y0 = 480
    ile = int(min(30, max(0, (t - 0.1) / 0.045)))
    for i in range(30):
        x, y = x0 + (i % kol) * (s + g), y0 + (i // kol) * (s + g)
        on = i < ile
        d.rounded_rectangle([x, y, x + s, y + s], radius=16, fill=(ZIELONY if on else (46, 48, 58)) + (255,))
        if on:
            f = f_anton(48)
            d.text((x + s / 2 - szer(d, "5", f) / 2, y + 18), "5", font=f, fill=CIEMNY + (255,))
    suma = 5 * ile
    fb = f_anton(110)
    tl = f"= {suma}"
    d.text((CX - szer(d, tl, fb) / 2, y0 + 5 * (s + g) + 20), tl, font=fb, fill=BIEL + (255,))
    fs = f_inter(32, False)
    tx = p.get("podpis", "30 dni po 5")
    d.text((CX - szer(d, tx, fs) / 2, 380), tx, font=fs, fill=SZARY + (255,))
    im.alpha_composite(nak)


def kubek(d, cx, cy, r, a):
    k = (236, 226, 210, int(255 * a))
    d.polygon([(cx - r, cy - r * 0.8), (cx + r, cy - r * 0.8), (cx + r * 0.75, cy + r), (cx - r * 0.75, cy + r)], fill=k)
    d.arc([cx + r * 0.6, cy - r * 0.4, cx + r * 1.4, cy + r * 0.4], -90, 90, fill=k, width=max(5, int(r * 0.15)))
    for dx in (-0.35, 0.05, 0.45):
        d.arc([cx + dx * r - r * 0.2, cy - r * 1.7, cx + dx * r + r * 0.2, cy - r * 0.95], 100, 260, fill=(200, 200, 206, int(200 * a)), width=4)


def scena_waga(im, t, dl, p, kt):
    """Waga: 150 opada ciezko (wydatek), 5 przy kubku kawy unosi sie lekko."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    ang = 0.22 * wej(t, 0.3, 0.6)
    cx, cy, L = CX, 700, 330
    d.polygon([(cx, cy), (cx - 50, 1150), (cx + 50, 1150)], fill=(90, 92, 102, int(255 * a)))
    lx, ly = cx - L * math.cos(ang), cy + L * math.sin(ang)
    rx, ry = cx + L * math.cos(ang), cy - L * math.sin(ang)
    d.line([lx, ly, rx, ry], fill=(200, 200, 206, int(255 * a)), width=12)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(200, 200, 206, int(255 * a)))
    # lewa szalka: 150 - wydatek
    d.line([lx, ly, lx, ly + 120], fill=(200, 200, 206, int(255 * a)), width=4)
    d.rounded_rectangle([lx - 120, ly + 120, lx + 120, ly + 270], radius=18, fill=(240, 120, 100, int(255 * a)))
    fb = f_anton(80)
    d.text((lx - szer(d, "150", fb) / 2, ly + 140), "150", font=fb, fill=CIEMNY + (int(255 * a),))
    fl = f_inter(32)
    tx = "wydatek"
    d.text((lx - szer(d, tx, fl) / 2, ly + 290), tx, font=fl, fill=BIEL + (int(255 * wej(t, 0.6, 0.3)),))
    # prawa szalka: 5 - drobne na kawe
    d.line([rx, ry, rx, ry + 120], fill=(200, 200, 206, int(255 * a)), width=4)
    kubek(d, rx - 60, ry + 190, 50, a)
    d.text((rx + 40, ry + 150), "5", font=fb, fill=ZIELONY + (int(255 * a),))
    tx2 = "drobne"
    d.text((rx - szer(d, tx2, fl) / 2, ry + 290), tx2, font=fl, fill=BIEL + (int(255 * wej(t, 0.6, 0.3)),))
    im.alpha_composite(nak)


def scena_slupki2(im, t, dl, p, kt):
    """Dowod: dwa slupki z badania."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    if tl:
        fb = dopasuj(d, tl, X1 - X0, 64, 36, f_anton)
        d.text((CX - szer(d, tl, fb) / 2, 300), tl, font=fb, fill=BIEL + (int(255 * a),))
    if p.get("podtytul"):
        fs = f_inter(30, False)
        d.text((CX - szer(d, p["podtytul"], fs) / 2, 390), p["podtytul"], font=fs, fill=SZARY + (int(255 * a),))
    dwa_slupki(d, t, p["wartosci"], p["etykiety"], [tuple(x) for x in p.get("kolory", [ZIELONY, (110, 112, 124)])],
               jedn=p.get("jedn", "%"))
    im.alpha_composite(nak)


def scena_przelicz(im, t, dl, p, kt):
    """Wniosek: metka '5 dziennie' obraca sie i pokazuje '150 miesiecznie' + ptaszek."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    q = wej(t, 0.3, 0.6)
    w = 360 * abs(math.cos(q * math.pi))
    pierwsza = q < 0.5
    l1, l2, kol = (p["przod"][0], p["przod"][1], ZIELONY) if pierwsza else (p["tyl"][0], p["tyl"][1], (240, 120, 100))
    if w > 20:
        metka(d, CX, 760, w, 380, l1, l2, kol, a)
    pz = pop(t, 1.1, 0.4)
    if pz > 0:
        ptaszek(d, CX + 220, 560, 70 * pz)
        linie_tekstu(d, p["linie"], CX, 1030, min(1, pz), px=70)
    im.alpha_composite(nak)


# ---------- wozek

def wozek(d, cx, cy, s, a, uchwyt="poziomy", t=0.0, kol=(200, 202, 210)):
    """Wozek z boku. uchwyt: 'poziomy' (zwykla raczka) albo 'pionowy' (dwa uchwyty zginajace rece)."""
    k = kol + (int(255 * a),)
    w = int(6 * s)
    pts = [(cx - 170 * s, cy - 120 * s), (cx + 150 * s, cy - 120 * s), (cx + 110 * s, cy + 40 * s), (cx - 140 * s, cy + 40 * s)]
    d.polygon(pts, outline=k, width=w)
    for i in range(1, 6):
        x = cx - 170 * s + i * 320 * s / 6
        d.line([x, cy - 120 * s, x - 6 * s * (1 if i < 3 else -1), cy + 40 * s], fill=k, width=max(2, w // 2))
    d.line([cx - 160 * s, cy - 40 * s, cx + 135 * s, cy - 40 * s], fill=k, width=max(2, w // 2))
    d.line([cx - 140 * s, cy + 40 * s, cx - 150 * s, cy + 100 * s, cx + 120 * s, cy + 100 * s], fill=k, width=w)
    for x in (cx - 120 * s, cx + 100 * s):
        r = 22 * s
        d.ellipse([x - r, cy + 100 * s, x + r, cy + 100 * s + 2 * r], outline=k, width=w)
        an = t * 6
        d.line([x, cy + 100 * s + r, x + r * 0.8 * math.cos(an), cy + 100 * s + r + r * 0.8 * math.sin(an)], fill=k, width=max(2, w // 2))
    hx, hy = cx - 170 * s, cy - 120 * s
    d.line([hx, hy, hx - 60 * s, hy - 70 * s], fill=k, width=w)
    if uchwyt == "poziomy":
        d.ellipse([hx - 80 * s, hy - 90 * s, hx - 40 * s, hy - 50 * s], fill=ZOLTY + (int(255 * a),))
    else:
        d.rounded_rectangle([hx - 75 * s, hy - 170 * s, hx - 45 * s, hy - 60 * s], radius=int(12 * s), fill=ZOLTY + (int(255 * a),))
    return hx - 60 * s, hy - 70 * s


def ramie(d, sx, sy, kat_ramie, kat_przedr, dl1, dl2, kol, a, gr=26):
    ex, ey = sx + dl1 * math.cos(kat_ramie), sy + dl1 * math.sin(kat_ramie)
    hx, hy = ex + dl2 * math.cos(kat_przedr), ey + dl2 * math.sin(kat_przedr)
    k = kol + (int(255 * a),)
    d.line([sx, sy, ex, ey], fill=k, width=gr)
    d.line([ex, ey, hx, hy], fill=k, width=gr)
    for x, y, r in ((sx, sy, gr * 0.9), (ex, ey, gr * 0.6), (hx, hy, gr * 0.8)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=k)
    return hx, hy


def scena_pytanie_wozek(im, t, dl, p, kt):
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, kt["akcent"])
    nak, d = warstwa()
    hx, hy = wozek(d, CX + 60, dol + 470, 1.5, 1.0, "pionowy", t)
    if 0.1 < t:
        r = 40 + 10 * math.sin(t * 6)
        d.ellipse([hx - 15 - r, hy - 80 - r, hx - 15 + r, hy - 80 + r], outline=kt["akcent"] + (220,), width=6)
    im.alpha_composite(nak)
    smuga(im, t)


def scena_ramiona(im, t, dl, p, kt):
    """Dwie postacie zwrocone w prawo. Lewa zgina ramie i przyciaga paczke do piersi (do siebie),
    prawa prostuje ramie i odsuwa paczke od siebie. Strzalki pokazuja kierunek."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    f = f_anton(56)
    q = wej(t, 0.3, 0.8)
    for i, (tx, kol) in enumerate(((p.get("lewy", "DO SIEBIE"), ZIELONY), (p.get("prawy", "OD SIEBIE"), (240, 120, 100)))):
        x = CX - 230 + i * 400
        d.text((x + 40 - szer(d, tx, f) / 2, 360), tx, font=f, fill=kol + (int(255 * a),))
        d.ellipse([x - 50, 520, x + 50, 620], fill=(200, 200, 206, int(255 * a)))
        d.rounded_rectangle([x - 70, 640, x + 70, 960], radius=40, fill=(200, 200, 206, int(255 * a)))
        if i == 0:
            # zgiete: przedramie wraca do piersi
            kp = -0.2 - q * 2.3
            hx, hy = ramie(d, x + 40, 690, 0.45, kp, 120, 110, kol, a)
            d.rounded_rectangle([hx - 34, hy - 34, hx + 34, hy + 34], radius=8, fill=ZOLTY + (int(255 * a),))
            strzalka(d, (x + 230, 1010), (x + 60, 1010), kol, a * q, grub=8)
        else:
            # proste: reka idzie od tulowia w prawo
            hx, hy = ramie(d, x + 40, 690, 0.25 - 0.2 * q, 0.05, 110, 100 + 30 * q, kol, a)
            d.rounded_rectangle([hx, hy - 34, hx + 68, hy + 34], radius=8, fill=ZOLTY + (int(255 * a),))
            strzalka(d, (x + 20, 1010), (x + 200, 1010), kol, a * q, grub=8)
    im.alpha_composite(nak)


def paragon(d, cx, ytop, w, h, kwota, a):
    ka = int(255 * a)
    d.rectangle([cx - w / 2, ytop, cx + w / 2, ytop + h], fill=(246, 244, 240, ka))
    for x in range(int(cx - w / 2), int(cx + w / 2), 20):
        d.polygon([(x, ytop + h), (x + 10, ytop + h + 12), (x + 20, ytop + h)], fill=(246, 244, 240, ka))
    for k in range(int((h - 120) / 34)):
        d.rounded_rectangle([cx - w / 2 + 24, ytop + 30 + k * 34, cx + w / 2 - 24 - (k % 3) * 30, ytop + 44 + k * 34], radius=5,
                            fill=(200, 200, 206, ka))
    f = f_anton(64)
    d.text((cx - szer(d, kwota, f) / 2, ytop + h - 86), kwota, font=f, fill=CIEMNY + (ka,))


def scena_paragony(im, t, dl, p, kt):
    """Dwa wozki, pod kazdym paragon; przy uchwytach zginajacych rece paragon jest dluzszy."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    for i, (uch, kw, hmax) in enumerate((("poziomy", p["kwoty"][0], 300), ("pionowy", p["kwoty"][1], 400))):
        x = CX - 190 + i * 380
        wozek(d, x + 30, 520, 0.75, a, uch, 0)
        et = p.get("etykiety", ["zwykła rączka", "uchwyty"])[i]
        fe = f_inter(28, False)
        d.text((x - szer(d, et, fe) / 2, 640), et, font=fe, fill=SZARY + (int(255 * a),))
        q = wej(t, 0.4 + i * 0.3, 0.7)
        if q > 0:
            paragon(d, x, 700, 250, 140 + (hmax - 140) * q, kw, 1.0)
    im.alpha_composite(nak)


def scena_wniosek_wozek(im, t, dl, p, kt):
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    wozek(d, CX + 40, 760, 1.3, a, "poziomy", t)
    pz = pop(t, 0.4, 0.4)
    if pz > 0:
        ptaszek(d, X1 - 120, 520, 80 * pz)
        linie_tekstu(d, p["linie"], CX, 1060, min(1, pz), px=70)
    im.alpha_composite(nak)


# ---------- palec kontra myszka

def sernik(d, cx, cy, r, a):
    ka = int(255 * a)
    d.polygon([(cx - r, cy + r * 0.5), (cx + r, cy + r * 0.5), (cx + r * 0.2, cy - r * 0.6)], fill=(250, 226, 160, ka))
    d.polygon([(cx - r, cy + r * 0.5), (cx + r, cy + r * 0.5), (cx + r, cy + r * 0.75), (cx - r, cy + r * 0.75)], fill=(180, 120, 70, ka))
    d.ellipse([cx - r * 0.1, cy - r * 0.75, cx + r * 0.3, cy - r * 0.35], fill=(220, 50, 60, ka))


def salatka(d, cx, cy, r, a):
    ka = int(255 * a)
    d.chord([cx - r, cy - r * 0.6, cx + r, cy + r * 0.9], 0, 180, fill=(220, 220, 230, ka))
    for dx, dy, kol in ((-0.5, -0.05, (240, 80, 70)), (0.0, -0.2, (120, 200, 90)), (0.45, 0.0, (250, 190, 60)), (-0.1, 0.1, (130, 80, 180))):
        d.ellipse([cx + dx * r - r * 0.25, cy + dy * r - r * 0.25, cx + dx * r + r * 0.25, cy + dy * r + r * 0.25], fill=kol + (ka,))


def ik_dlon(d, cx, cy, r, kol, a):
    k = kol + (int(255 * a),)
    d.rounded_rectangle([cx - r * 0.18, cy - r, cx + r * 0.18, cy], radius=int(r * 0.18), fill=k)
    d.rounded_rectangle([cx - r * 0.55, cy - r * 0.2, cx + r * 0.55, cy + r * 0.8], radius=int(r * 0.3), fill=k)


def ik_mysz(d, cx, cy, r, kol, a):
    k = kol + (int(255 * a),)
    d.rounded_rectangle([cx - r * 0.55, cy - r, cx + r * 0.55, cy + r], radius=int(r * 0.55), outline=k, width=max(5, int(r * 0.12)))
    d.line([cx, cy - r, cx, cy - r * 0.2], fill=k, width=max(4, int(r * 0.1)))


def scena_pytanie_palec(im, t, dl, p, kt):
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, kt["akcent"])

    def ekran(im2, box, tt, a):
        x0, y0, x1, y1 = box
        n2, d2 = warstwa()
        cxx = (x0 + x1) / 2
        for j, rys in enumerate((sernik, salatka)):
            yy = y0 + 150 + j * 250
            d2.rounded_rectangle([x0 + 24, yy - 100, x1 - 24, yy + 110], radius=20, fill=(255, 255, 255, int(255 * a)),
                                 outline=(220, 220, 226, int(255 * a)), width=3)
            rys(d2, cxx, yy, 70, a)
        im2.alpha_composite(n2)
    box = telefon(im, CX, dol + 470, 0.95, 1.0, ekran, t)
    nak, d = warstwa()
    tap = wcisk_fazy(t, 0.15, 0.9)
    px, py = (box[0] + box[2]) / 2 + 60, box[1] + 170
    palec(d, px, py, 1.0, tap)
    ik_dlon(d, px + 30, py + 110 - 20 * tap, 60, (236, 200, 170), 1.0)
    im.alpha_composite(nak)
    smuga(im, t)


def scena_siegniecie(im, t, dl, p, kt):
    """Palec dotyka sernika, a ten 'wychodzi z ekranu' w strone reki."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    q = wej(t, 0.4, 0.9)
    d.rounded_rectangle([CX - 220, 480, CX + 220, 1180], radius=50, fill=(34, 34, 40, int(255 * a)))
    d.rounded_rectangle([CX - 200, 500, CX + 200, 1160], radius=40, fill=(246, 244, 240, int(255 * a)))
    sernik(d, CX, 760 - 120 * q, 90 + 90 * q, a)
    ik_dlon(d, CX + 60, 1000 - 120 * q, 90, (236, 200, 170), a)
    if q > 0.6:
        tx = p.get("napis", "JAK SIĘGNIĘCIE RĘKĄ")
        f = dopasuj(d, tx, X1 - X0, 60, 36, f_anton)
        d.text((CX - szer(d, tx, f) / 2, 330), tx, font=f, fill=BIEL + (int(255 * wej(t, 1.0, 0.3)),))
    im.alpha_composite(nak)


def scena_palec_mysz(im, t, dl, p, kt):
    """Dowod: sernik wybrany - dotyk 95%, myszka 73%."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    sernik(d, CX, 380, 70, a)
    fs = f_inter(32, False)
    tx = p.get("podpis", "wybrało sernik zamiast sałatki")
    d.text((CX - szer(d, tx, fs) / 2, 470), tx, font=fs, fill=SZARY + (int(255 * a),))
    dwa_slupki(d, t, p["wartosci"], p["etykiety"], [ZIELONY, (110, 112, 124)], y_dol=1150, wys_max=440)
    im.alpha_composite(nak)


def scena_policz(im, t, dl, p, kt):
    """Wniosek: palec zawisa nad 'Kup', odliczanie 1-2-3."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    bx0, by0, bx1, by1 = CX - 230, 820, CX + 230, 950
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=30, fill=(255, 92, 40, int(255 * a)))
    f = f_inter(54)
    d.text((CX - szer(d, "Kup", f) / 2, by0 + 32), "Kup", font=f, fill=BIEL + (int(255 * a),))
    ik_dlon(d, CX + 150, by1 + 150 + 10 * math.sin(t * 3), 80, (236, 200, 170), a)
    n = min(3, int(max(0, t - 0.3) / 0.5) + 1) if t > 0.3 else 0
    if n:
        tl = str(n)
        pz = pop(t, 0.3 + (n - 1) * 0.5, 0.3)
        fb = f_anton(max(1, int(200 * max(pz, 0.01))))
        d.text((CX - szer(d, tl, fb) / 2, 420), tl, font=fb, fill=ZOLTY + (255,))
    im.alpha_composite(nak)


# ---------- abonament

def ik_usluga(d, x, y, s, kol, typ, a):
    ka = int(255 * a)
    d.rounded_rectangle([x, y, x + s, y + s], radius=int(s * 0.22), fill=kol + (ka,))
    c = (x + s / 2, y + s / 2)
    if typ == 0:
        d.polygon([(c[0] - s * 0.15, c[1] - s * 0.2), (c[0] - s * 0.15, c[1] + s * 0.2), (c[0] + s * 0.2, c[1])], fill=BIEL + (ka,))
    elif typ == 1:
        d.ellipse([c[0] - s * 0.2, c[1] + s * 0.02, c[0] - s * 0.02, c[1] + s * 0.2], fill=BIEL + (ka,))
        d.line([c[0] - s * 0.03, c[1] + s * 0.1, c[0] - s * 0.03, c[1] - s * 0.22, c[0] + s * 0.18, c[1] - s * 0.16], fill=BIEL + (ka,), width=max(3, int(s * 0.06)))
    else:
        d.ellipse([c[0] - s * 0.25, c[1] - s * 0.05, c[0] + s * 0.05, c[1] + s * 0.2], fill=BIEL + (ka,))
        d.ellipse([c[0] - s * 0.1, c[1] - s * 0.2, c[0] + s * 0.25, c[1] + s * 0.2], fill=BIEL + (ka,))


USLUGI = [((230, 60, 70), 0, "Filmy"), ((40, 190, 100), 1, "Muzyka"), ((70, 130, 240), 2, "Chmura"), ((240, 160, 40), 0, "Kursy")]


def scena_pytanie_abonament(im, t, dl, p, kt):
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, kt["akcent"])

    def ekran(im2, box, tt, a):
        x0, y0, x1, y1 = box
        n2, d2 = warstwa()
        for j, (kol, typ, nazwa) in enumerate(USLUGI):
            pj = 1.0 if j == 0 else wej(tt, j * 0.35, 0.35)
            if pj <= 0:
                continue
            yy = y0 + 80 + j * 130 - 30 * (1 - pj)
            d2.rounded_rectangle([x0 + 18, yy, x1 - 18, yy + 110], radius=20, fill=(255, 255, 255, int(255 * a * pj)))
            ik_usluga(d2, x0 + 32, yy + 20, 70, kol, typ, a * pj)
            f = f_inter(26)
            d2.text((x0 + 118, yy + 18), nazwa, font=f, fill=(40, 40, 46, int(255 * pj)))
            d2.text((x0 + 118, yy + 58), "-29,99 zł", font=f_inter(26), fill=(220, 60, 60, int(255 * pj)))
        im2.alpha_composite(n2)
    telefon(im, CX, dol + 470, 0.95, 1.0, ekran, t)
    smuga(im, t)


def scena_schodza(im, t, dl, p, kt):
    """Miesiace mijaja, a monety same spadaja z konta - okienko 'decyzja' nigdy sie nie pojawia."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    mies = ["sty", "lut", "mar", "kwi", "maj", "cze"]
    krok = 120
    x0 = CX - krok * 2.5
    for i, m in enumerate(mies):
        x = x0 + i * krok
        on = t > 0.2 + i * 0.3
        d.rounded_rectangle([x - 50, 420, x + 50, 520], radius=16, fill=((70, 72, 86) if not on else (90, 60, 64)) + (int(255 * a),))
        f = f_inter(30)
        d.text((x - szer(d, m, f) / 2, 450), m, font=f, fill=BIEL + (int(255 * a),))
        q = (t - (0.2 + i * 0.3)) / 0.6
        if 0 < q < 1:
            y = 540 + 520 * q
            d.ellipse([x - 32, y - 32, x + 32, y + 32], fill=ZOLTY + (int(255 * (1 - q * 0.3)),))
    d.rounded_rectangle([CX - 300, 1080, CX + 300, 1200], radius=24, fill=(40, 42, 52, int(255 * a)))
    saldo = 1000 - 30 * min(6, max(0, int((t - 0.2) / 0.3) + (1 if t > 0.2 else 0)))
    fb = f_anton(64)
    tx = f"konto: {saldo}"
    d.text((CX - szer(d, tx, fb) / 2, 1100), tx, font=fb, fill=BIEL + (int(255 * a),))
    fs = f_inter(30, False)
    t2 = p.get("podpis", "decyzja? nigdy nie pada")
    d.text((CX - szer(d, t2, fs) / 2, 1230), t2, font=fs, fill=SZARY + (int(255 * wej(t, 0.8, 0.3)),))
    im.alpha_composite(nak)


def scena_przeglad(im, t, dl, p, kt):
    """Wniosek: raz w miesiacu lista subskrypcji, zbedne skreslone."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    budzik(d, CX, 400, 50 * max(0.01, pop(t, 0.05, 0.4)), 1.0, ZOLTY)
    x0, x1 = CX - 300, CX + 300
    for j, (kol, typ, nazwa) in enumerate(USLUGI):
        y = 520 + j * 150
        d.rounded_rectangle([x0, y, x1, y + 120], radius=22, fill=(40, 42, 52, int(255 * a)))
        ik_usluga(d, x0 + 20, y + 20, 80, kol, typ, a)
        f = f_inter(36)
        d.text((x0 + 130, y + 38), nazwa, font=f, fill=BIEL + (int(255 * a),))
        zostaje = j in (0, 2)
        q = wej(t, 0.5 + j * 0.25, 0.3)
        if q > 0:
            if zostaje:
                ptaszek(d, x1 - 60, y + 60, 34 * q)
            else:
                d.line([x0 + 120, y + 62, x0 + 120 + (x1 - x0 - 200) * q, y + 62], fill=CZERW + (255,), width=8)
                krzyzyk(d, x1 - 60, y + 60, 26, 1.0, q)
    im.alpha_composite(nak)


SCENY_MARKETING = {"pytanie_dziennie": scena_pytanie_dziennie, "ta_sama": scena_ta_sama, "waga": scena_waga,
                   "slupki2": scena_slupki2, "przelicz": scena_przelicz,
                   "pytanie_wozek": scena_pytanie_wozek, "ramiona": scena_ramiona, "paragony": scena_paragony,
                   "wniosek_wozek": scena_wniosek_wozek,
                   "pytanie_palec": scena_pytanie_palec, "siegniecie": scena_siegniecie, "palec_mysz": scena_palec_mysz,
                   "policz": scena_policz,
                   "pytanie_abonament": scena_pytanie_abonament, "schodza": scena_schodza, "przeglad": scena_przeglad}

SCENY = {"pytanie": scena_pytanie, "magazyn": scena_magazyn, "wtyczka": scena_wtyczka,
         "firmy": scena_firmy, "wniosek": scena_wniosek, "cta": scena_cta,
         "pytanie_dymek": scena_pytanie_dymek, "aplikacje": scena_aplikacje,
         "zrodla": scena_zrodla, "mikro_oko": scena_mikro_oko,
         "pytanie_okno": scena_pytanie_okno, "ludzie": scena_ludzie, "czyszczenie": scena_czyszczenie,
         "obserwatorzy": scena_obserwatorzy, "dom_siec": scena_dom_siec,
         "pytanie_dokument": scena_pytanie_dokument, "klauzula": scena_klauzula, "czas": scena_czas, "sprawdz": scena_sprawdz,
         "pytanie_baner": scena_pytanie_baner, "kafelki": scena_kafelki, "dwa_banery": scena_dwa_banery, "ustawienia": scena_ustawienia}
SCENY.update(SCENY_PRZYCISK)
SCENY.update(SCENY_1411)
SCENY.update(SCENY_MARKETING)


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
    # BRAMKA: sceny musza startowac po kolei - inaczej slowo z wczesniejszego zdania
    # (np. "reklame" w pytaniu) odpala scene za wczesnie i przykrywa poprzednia
    for (a, sa), (b, sb) in zip(sceny, sceny[1:]):
        if b <= a:
            raise SystemExit(f"scena '{sb['typ']}' (od {b:.2f} s) startuje przed '{sa['typ']}' ({a:.2f} s) - uzyj 'slowo#2'")
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
        # na scenie CTA nazwa stoi duzo - znak wodny bylby dublem
        if not any(sc["typ"] == "cta" and od <= t for od, sc, do in sceny):
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
