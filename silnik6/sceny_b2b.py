"""Sceny silnika 6 do rolek B2B (od 13.11: wlasciciel firmy, specjalista od reklam tlumaczy).
Rejestruje sie w silnik6.SCENY przy imporcie."""
import math
import silnik6 as s6
from silnik6 import (warstwa, pytanie_u_gory, okno_przegladarki, czlowiek, ik_oko, ptaszek, linie_tekstu,
                     strzalka, krzyzyk, pigulka, telefon, wej, pop, szer, dopasuj, f_anton, f_inter,
                     CX, X0, X1, BIEL, SZARY, ZIELONY, ZOLTY, CIEMNY)

CZERW = (240, 110, 100)
SZ_CIEMNY = (70, 72, 82)


def _spinner(d, cx, cy, r, t, a, kol=BIEL):
    for i in range(10):
        ang = t * 6 + i * 2 * math.pi / 10
        al = int(255 * a * (0.25 + 0.75 * i / 9))
        x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=kol + (al,))


def _strona(d, x0, y0, x1, y1, a, glowna_p=1.0, bok_p=1.0, akc=ZOLTY, ramka_glowna=False):
    """Okno przegladarki: glowna kolumna (lewa, szeroka) i boczny panel (prawy, waski)."""
    okno_przegladarki(d, x0, y0, x1, y1, a)
    gx0, gx1 = x0 + 30, x0 + int((x1 - x0) * 0.66)
    bx0, bx1 = gx1 + 24, x1 - 30
    top = y0 + 100
    if glowna_p > 0:
        d.rounded_rectangle([gx0, top, gx1, top + 170], radius=14, fill=(90, 92, 104, int(255 * a * glowna_p)))
        for i in range(5):
            d.rounded_rectangle([gx0, top + 200 + i * 44, gx1 - (i % 2) * 60, top + 222 + i * 44], radius=8,
                                fill=(150, 152, 162, int(255 * a * glowna_p)))
    if bok_p > 0:
        for i in range(3):
            d.rounded_rectangle([bx0, top + i * 130, bx1, top + i * 130 + 110], radius=12,
                                fill=(120, 122, 134, int(255 * a * bok_p)))
    if ramka_glowna:
        d.rounded_rectangle([gx0 - 12, top - 12, gx1 + 12, top + 432], radius=18, outline=akc + (int(255 * a),), width=6)
    return (gx0, top, gx1, top + 420), (bx0, top, bx1, top + 370)


# ---------------------------------------------------------------- a1: szybkosc strony

def scena_pytanie_strona(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, y0, x1, y1 = X0 + 20, dol + 70, X1 - 20, dol + 640
    q = wej(t, 0.0, 0.5)
    g, b = _strona(d, x0, y0, x1, y1, 1.0, glowna_p=0.25, bok_p=0.25)
    _spinner(d, (g[0] + g[2]) / 2, (g[1] + g[3]) / 2, 46, t, 1.0)
    # pasek ladowania u dolu okna
    pw = (x1 - x0 - 60) * (0.15 + 0.5 * min(1.0, t / 3))
    d.rounded_rectangle([x0 + 30, y1 - 40, x1 - 30, y1 - 24], radius=8, fill=(60, 60, 70, 255))
    d.rounded_rectangle([x0 + 30, y1 - 40, x0 + 30 + pw, y1 - 24], radius=8, fill=akc + (int(255 * q),))
    im.alpha_composite(nak)


def scena_najpierw(im, t, dl, p, kt):
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    x0, y0, x1, y1 = X0 + 20, 470, X1 - 20, 1040
    g, b = _strona(d, x0, y0, x1, y1, a, glowna_p=1.0, bok_p=0.35, akc=akc, ramka_glowna=t > 0.3)
    po = pop(t, 0.2, 0.4)
    if po > 0:
        ik_oko(d, CX, 360, 70 * po, akc, 1.0)
        strzalka(d, (CX - 40, 420), ((g[0] + g[2]) / 2, g[1] - 20), akc, min(1.0, po), grub=8)
    if t > 0.6:
        f = f_anton(46)
        tx = p.get("napis", "TO WIDZI NAJPIERW")
        pigulka(d, (g[0] + g[2]) // 2, g[3] + 40, tx, f, akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_bok_panel(im, t, dl, p, kt):
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    x0, y0, x1, y1 = X0 + 20, 470, X1 - 20, 1040
    bok_p = 0.2 if t < 0.9 else min(1.0, 0.2 + (t - 0.9) / 0.3)    # boczny panel doladowuje sie pozniej
    g, b = _strona(d, x0, y0, x1, y1, a, glowna_p=1.0, bok_p=bok_p)
    # znacznik opoznienia nad bocznym panelem
    po = pop(t, 0.15, 0.4)
    if po > 0:
        f = f_anton(int(56 * po) or 1)
        tx = "+0,25 s"
        d.text(((b[0] + b[2]) / 2 - szer(d, tx, f) / 2, y0 - 90), tx, font=f, fill=akc + (255,))
    if t > 1.2:
        f2 = f_anton(54)
        pigulka(d, CX, y1 + 30, "SPRZEDAŻ BEZ ZMIAN", f2, (70, 72, 82, 240), BIEL + (255,))
    im.alpha_composite(nak)


def scena_szybciej(im, t, dl, p, kt):
    """100 ms szybciej -> +0,6% przychodu: stoper i licznik."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    f = f_anton(60)
    tx = "-100 ms"
    d.text((CX - szer(d, tx, f) / 2, 300), tx, font=f, fill=BIEL + (int(255 * a),))
    # stoper
    cx, cy, r = CX, 560, 130
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BIEL + (int(255 * a),), width=10)
    d.rounded_rectangle([cx - 24, cy - r - 46, cx + 24, cy - r - 10], radius=6, fill=BIEL + (int(255 * a),))
    ang = -math.pi / 2 + min(1.0, t / 1.0) * 2 * math.pi * 0.85
    d.line([cx, cy, cx + r * 0.8 * math.cos(ang), cy + r * 0.8 * math.sin(ang)], fill=akc + (int(255 * a),), width=10)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=akc + (int(255 * a),))
    t06 = kt["czas_slowa"](p.get("liczba_od", "0,6%")) - kt["od"] - 0.1
    pz = pop(t, t06, 0.45)
    if pz > 0:
        q = min(1.0, (t - t06) / 0.5)
        v = 0.6 * (1 - (1 - q) ** 3)
        f2 = f_anton(max(1, int(150 * pz)))
        tx2 = f"+{v:.1f}%".replace(".", ",")
        d.text((CX - szer(d, tx2, f2) / 2, 760), tx2, font=f2, fill=ZIELONY + (255,))
        f3 = f_inter(36, False)
        tx3 = "przychodu"
        d.text((CX - szer(d, tx3, f3) / 2, 960), tx3, font=f3, fill=SZARY + (255,))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- a2: reklama na wlasna nazwe

def _wynik(d, x0, y, x1, a, reklama, akc):
    d.rounded_rectangle([x0, y, x1, y + 120], radius=16, fill=(52, 52, 62, int(255 * a)))
    if reklama:
        f = f_inter(26)
        pigulka(d, x0 + 80, y + 18, "Reklama", f, akc + (int(255 * a),), CIEMNY + (int(255 * a),), pad=(14, 6))
    d.rounded_rectangle([x0 + 24, y + 62, x1 - 120, y + 80], radius=8, fill=(170, 172, 182, int(255 * a)))
    d.rounded_rectangle([x0 + 24, y + 92, x1 - 220, y + 106], radius=7, fill=(120, 122, 132, int(255 * a)))


def scena_pytanie_marka(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, y0, x1, y1 = X0 + 20, dol + 70, X1 - 20, dol + 640
    okno_przegladarki(d, x0, y0, x1, y1, 1.0)
    # pasek wyszukiwania z wpisywana nazwa firmy
    d.rounded_rectangle([x0 + 40, y0 + 100, x1 - 40, y0 + 180], radius=40, fill=(246, 244, 240, 255))
    tx = "twoja firma"
    n = int(len(tx) * min(1.0, t / 1.2))
    f = f_inter(40, False)
    d.text((x0 + 80, y0 + 116), tx[:n], font=f, fill=CIEMNY + (255,))
    if int(t * 2) % 2 == 0:
        xc = x0 + 82 + szer(d, tx[:n], f)
        d.rectangle([xc, y0 + 118, xc + 4, y0 + 162], fill=CIEMNY + (255,))
    if t > 1.3:
        q = wej(t, 1.3, 0.3)
        _wynik(d, x0 + 40, y0 + 220, x1 - 40, q, True, akc)
        _wynik(d, x0 + 40, y0 + 370, x1 - 40, wej(t, 1.5, 0.3), False, akc)
    im.alpha_composite(nak)


def _sklep(d, cx, cy, s, a, kol=(90, 92, 104), akc=ZOLTY):
    d.rectangle([cx - 110 * s, cy - 60 * s, cx + 110 * s, cy + 90 * s], fill=kol + (int(255 * a),))
    for i in range(5):
        k = (CZERW if i % 2 == 0 else BIEL) + (int(255 * a),)
        d.rectangle([cx - 120 * s + i * 48 * s, cy - 100 * s, cx - 120 * s + (i + 1) * 48 * s, cy - 60 * s], fill=k)
    d.rectangle([cx - 30 * s, cy + 10 * s, cx + 30 * s, cy + 90 * s], fill=(30, 30, 36, int(255 * a)))


def scena_szuka(im, t, dl, p, kt):
    """Kto wpisuje nazwe, i tak idzie do ciebie: dwie drogi (reklama, darmowy wynik) do tych samych drzwi."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, CX, 420, 90, BIEL, a)
    _sklep(d, CX, 960, 1.3, a, akc=akc)
    f = f_inter(30)
    p1 = wej(t, 0.3, 0.6)
    p2 = wej(t, 0.7, 0.6)
    strzalka(d, (CX - 60, 520), (CX - 90, 820), akc, a, grub=9, postep=p1)
    strzalka(d, (CX + 60, 520), (CX + 90, 820), ZIELONY, a, grub=9, postep=p2)
    if p1 > 0.5:
        pigulka(d, CX - 230, 640, "reklama", f, akc + (240,), CIEMNY + (255,), pad=(18, 8))
    if p2 > 0.5:
        pigulka(d, CX + 250, 640, "darmowy wynik", f, ZIELONY + (240,), CIEMNY + (255,), pad=(18, 8))
    im.alpha_composite(nak)


def scena_region(im, t, dl, p, kt):
    """Test: reklame na nazwe wylacz w jednym regionie i porownaj z reszta."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    f = f_anton(56)
    tx = "TEST W JEDNYM REGIONIE"
    fb = dopasuj(d, tx, X1 - X0, 58, 36, f_anton)
    d.text((CX - szer(d, tx, fb) / 2, 300), tx, font=fb, fill=BIEL + (int(255 * a),))
    kol, rz = 3, 2
    w, h = 220, 200
    gx0 = CX - (kol * w + (kol - 1) * 24) / 2
    off = 2
    for i in range(kol * rz):
        x = gx0 + (i % kol) * (w + 24)
        y = 420 + (i // kol) * (h + 24)
        wyl = i == off and t > 0.6
        k = (60, 62, 72) if wyl else (90, 92, 104)
        d.rounded_rectangle([x, y, x + w, y + h], radius=20, fill=k + (int(255 * a),),
                            outline=(akc if wyl else (120, 122, 134)) + (int(255 * a),), width=5 if wyl else 2)
        # przelacznik
        on = not wyl
        tx0, ty0 = x + w / 2 - 50, y + h / 2 - 26
        d.rounded_rectangle([tx0, ty0, tx0 + 100, ty0 + 52], radius=26,
                            fill=(ZIELONY if on else (110, 112, 124)) + (int(255 * a),))
        kx = tx0 + (74 if on else 26)
        d.ellipse([kx - 20, ty0 + 6, kx + 20, ty0 + 46], fill=BIEL + (int(255 * a),))
    if t > 1.0:
        f2 = f_anton(48)
        pigulka(d, CX, 900, "PORÓWNAJ SPRZEDAŻ", f2, akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- a3: pomiar reklam

def scena_pytanie_raport(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    y0 = dol + 90
    # lewy panel: wykres w raporcie mocno w gore
    lx0, lx1 = X0 + 10, CX - 20
    rx0, rx1 = CX + 20, X1 - 10
    for (x0, x1, tyt) in ((lx0, lx1, "RAPORT"), (rx0, rx1, "KASA")):
        d.rounded_rectangle([x0, y0, x1, y0 + 460], radius=24, fill=(40, 40, 48, 235), outline=(80, 80, 90, 255), width=3)
        f = f_anton(44)
        d.text(((x0 + x1) / 2 - szer(d, tyt, f) / 2, y0 + 24), tyt, font=f, fill=BIEL + (255,))
    q = min(1.0, t / 1.4)
    pts = [(lx0 + 40 + i * (lx1 - lx0 - 80) / 5, y0 + 400 - (i / 5) ** 1.6 * 300 * q) for i in range(6)]
    d.line(pts, fill=ZIELONY + (255,), width=10, joint="curve")
    strzalka(d, pts[-2], (pts[-1][0] + 4, pts[-1][1] - 30), ZIELONY, 1.0, grub=10)
    # prawy: male slupki prawie bez zmian
    for i in range(4):
        hh = 70 + i * 12 * q
        x = rx0 + 40 + i * 70
        d.rounded_rectangle([x, y0 + 400 - hh, x + 46, y0 + 400], radius=8, fill=(150, 152, 162, 255))
    im.alpha_composite(nak)


def scena_kupiliby(im, t, dl, p, kt):
    """Reklame widza tez ci, ktorzy kupiliby i bez niej - zolci ludzie z torbami."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    kol, rz = 6, 4
    krok = 110
    gx0 = CX - (kol - 1) * krok / 2
    kupiliby = {1, 4, 7, 9, 14, 16, 20, 22}
    pk = wej(t, 0.8, 0.5)
    for i in range(kol * rz):
        x = gx0 + (i % kol) * krok
        y = 430 + (i // kol) * 140
        k = BIEL
        if i in kupiliby and pk > 0:
            k = tuple(int(BIEL[j] + (akc[j] - BIEL[j]) * pk) for j in range(3))
        czlowiek(d, x, y, 44, k, a)
        if i in kupiliby and pk > 0.5:
            d.rounded_rectangle([x + 22, y + 4, x + 50, y + 34], radius=5, fill=akc + (255,))
    # glosnik reklamy nad tlumem
    po = pop(t, 0.1, 0.4)
    if po > 0:
        f = f_anton(46)
        pigulka(d, CX, 300, "WIDZĄ REKLAMĘ", f, (70, 72, 82, 240), BIEL + (255,))
    if pk > 0.5:
        f2 = f_anton(46)
        pigulka(d, CX, 1000, "KUPILIBY I TAK", f2, akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_grupa(im, t, dl, p, kt):
    """Grupa kontrolna: polowa widzi reklame, polowa nie - roznica to efekt reklamy."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    for j, (cx, tyt, rekl) in enumerate(((CX - 200, "WIDZĄ", True), (CX + 200, "NIE WIDZĄ", False))):
        pj = wej(t, 0.1 + j * 0.25, 0.4)
        d.rounded_rectangle([cx - 170, 400, cx + 170, 860], radius=24, fill=(40, 40, 48, int(235 * pj)),
                            outline=(akc if rekl else (110, 112, 124)) + (int(255 * pj),), width=4)
        f = f_anton(44)
        d.text((cx - szer(d, tyt, f) / 2, 420), tyt, font=f, fill=BIEL + (int(255 * pj),))
        for i in range(6):
            czlowiek(d, cx - 90 + (i % 3) * 90, 560 + (i // 3) * 130, 40, BIEL, pj)
        # ikona reklamy (prostokat z trojkatem play), skreslona po prawej
        d.rounded_rectangle([cx - 50, 790, cx + 50, 840], radius=8, fill=(akc if rekl else (110, 112, 124)) + (int(255 * pj),))
        if not rekl and pj > 0.5:
            krzyzyk(d, cx, 815, 40, pj, 1.0)
    if t > 1.0:
        f2 = f_anton(46)
        pigulka(d, CX, 920, "RÓŻNICA = EFEKT REKLAMY", f2, akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_strona": scena_pytanie_strona, "najpierw": scena_najpierw, "bok_panel": scena_bok_panel,
    "szybciej": scena_szybciej,
    "pytanie_marka": scena_pytanie_marka, "szuka": scena_szuka, "region": scena_region,
    "pytanie_raport": scena_pytanie_raport, "kupiliby": scena_kupiliby, "grupa": scena_grupa,
})
