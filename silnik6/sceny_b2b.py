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
    n = len(tx)   # wpisane od pierwszej klatki - okladka pokazuje, czego szuka klient
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


# ---------------------------------------------------------------- wspolne: dwa wzrosty na slowach

def scena_dwa_wzrosty(im, t, dl, p, kt):
    """Tytul + dwie duze liczby wyskakujace na slowach lektora (np. +20% otwarc, +31% leadow)."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    if tl:
        fb = dopasuj(d, tl, X1 - X0, 60, 36, f_anton)
        d.text((CX - szer(d, tl, fb) / 2, 300), tl, font=fb, fill=BIEL + (int(255 * a),))
    if p.get("podtytul"):
        fs = f_inter(30, False)
        d.text((CX - szer(d, p["podtytul"], fs) / 2, 390), p["podtytul"], font=fs, fill=SZARY + (int(255 * a),))
    if p.get("firmy"):
        # male budynki firm trzymaja kadr, zanim padnie pierwsza liczba
        tp = kt["czas_slowa"](p["pozycje"][0]["od"]) - kt["od"] - 0.1
        fa = a * (1 - wej(t, tp, 0.3))
        if fa > 0:
            for j in range(8):
                _sklep(d, CX - 330 + (j % 4) * 220, 560 + (j // 4) * 260, 0.6, fa)
    if p.get("wykres"):
        tp = kt["czas_slowa"](p["pozycje"][0]["od"]) - kt["od"] - 0.1
        wa = a * (1 - wej(t, tp, 0.3))
        if wa > 0:
            vals = [0.3, 0.25, 1.0, 0.22, 0.3]
            w = (X1 - X0 - 120) / len(vals)
            for i, v in enumerate(vals):
                d.rounded_rectangle([X0 + 60 + i * w + 10, 900 - 420 * v, X0 + 60 + (i + 1) * w - 10, 900], radius=10,
                                    fill=(kt["akcent"] if i == 2 else (120, 122, 134)) + (int(255 * wa),))
    for i, poz in enumerate(p["pozycje"]):
        t0 = kt["czas_slowa"](poz["od"]) - kt["od"] - 0.1 if poz.get("od") else 0.2 + i * 0.4
        pz = pop(t, t0, 0.45)
        if pz <= 0:
            continue
        y = 500 + i * 300
        f = f_anton(max(1, int(150 * pz)))
        d.text((CX - szer(d, poz["liczba"], f) / 2, y), poz["liczba"], font=f, fill=(ZIELONY if i == 0 else akc) + (255,))
        f2 = f_inter(40)
        d.text((CX - szer(d, poz["podpis"], f2) / 2, y + 190), poz["podpis"], font=f2, fill=BIEL + (int(255 * min(1, pz)),))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- b1: imie w temacie maila

def _skrzynka(d, x0, y0, x1, n, a, wyroznij=None, akc=ZOLTY, imie_p=1.0):
    for i in range(n):
        y = y0 + i * 100
        wyr = i == wyroznij
        d.rounded_rectangle([x0, y, x1, y + 84], radius=14,
                            fill=((60, 60, 70) if not wyr else (70, 66, 50)) + (int(255 * a),),
                            outline=(akc + (int(255 * a * imie_p),)) if wyr else None, width=4 if wyr else 0)
        d.ellipse([x0 + 16, y + 18, x0 + 64, y + 66], fill=(120, 122, 134, int(255 * a)))
        if wyr:
            f = f_inter(30)
            d.text((x0 + 84, y + 12), "Anna,", font=f, fill=akc + (int(255 * a * imie_p),))
            d.rounded_rectangle([x0 + 84 + szer(d, "Anna, ", f), y + 22, x1 - 40, y + 40], radius=8, fill=(200, 200, 206, int(255 * a)))
        else:
            d.rounded_rectangle([x0 + 84, y + 22, x1 - 60 - (i % 3) * 40, y + 40], radius=8, fill=(170, 172, 182, int(255 * a)))
        d.rounded_rectangle([x0 + 84, y + 52, x1 - 140, y + 64], radius=6, fill=(110, 112, 124, int(255 * a)))


def scena_pytanie_mail(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, y0, x1, y1 = X0 + 20, dol + 70, X1 - 20, dol + 640
    okno_przegladarki(d, x0, y0, x1, y1, 1.0)
    _skrzynka(d, x0 + 30, y0 + 100, x1 - 30, 4, 1.0, wyroznij=1, akc=akc, imie_p=1.0)
    im.alpha_composite(nak)


def scena_do_jednej(im, t, dl, p, kt):
    """Mail z imieniem = do jednej osoby; bez imienia = do calej bazy."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    # lewa: koperta -> jedna osoba (akcent); prawa: koperta -> tlum (szary)
    for j, cx in enumerate((CX - 200, CX + 200)):
        pj = wej(t, 0.1 + j * 0.3, 0.4)
        ex, ey = cx, 430
        d.rounded_rectangle([ex - 80, ey - 52, ex + 80, ey + 52], radius=10, fill=((akc if j == 0 else (150, 152, 162)) + (int(255 * pj),)))
        d.line([ex - 80, ey - 50, ex, ey + 6, ex + 80, ey - 50], fill=(30, 30, 36, int(255 * pj)), width=6)
        strzalka(d, (ex, ey + 70), (ex, ey + 200), (akc if j == 0 else (150, 152, 162)), pj, grub=8)
        if j == 0:
            czlowiek(d, cx, 740, 90, akc, pj)
            f = f_anton(44)
            pigulka(d, cx, 860, "DO CIEBIE", f, akc + (int(240 * pj),), CIEMNY + (int(255 * pj),))
        else:
            for i in range(9):
                czlowiek(d, cx - 90 + (i % 3) * 90, 660 + (i // 3) * 90, 34, (150, 152, 162), pj)
            f = f_anton(44)
            pigulka(d, cx, 940, "DO BAZY", f, (70, 72, 82, int(240 * pj)), BIEL + (int(255 * pj),))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- b2: reklama z ogladanym produktem

def _karta_reklamy(d, x0, y0, x1, y1, a, produkt, akc):
    d.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=(52, 52, 62, int(255 * a)))
    f = f_inter(24)
    pigulka(d, x0 + 90, y0 + 16, "Reklama", f, (90, 92, 104, int(255 * a)), BIEL + (int(255 * a),), pad=(12, 5))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 20
    if produkt:   # pudelko z produktem
        d.rounded_rectangle([cx - 70, cy - 60, cx + 70, cy + 60], radius=12, fill=akc + (int(255 * a),))
        d.rectangle([cx - 70, cy - 10, cx + 70, cy + 10], fill=(30, 30, 36, int(110 * a)))
    else:         # znak marki (zuk)
        d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=akc + (int(255 * a),), width=12)
        pts = [(cx + 42 * math.cos(-math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45),
                cy + 42 * math.sin(-math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45)) for k in range(10)]
        d.polygon(pts, fill=akc + (int(255 * a),))


def scena_pytanie_retarget(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)

    def ekran(im2, box, tt, a):
        x0, y0, x1, y1 = box
        nak, d = warstwa()
        for i in range(3):
            d.rounded_rectangle([x0 + 24, y0 + 70 + i * 46, x1 - 24 - i * 40, y0 + 92 + i * 46], radius=8, fill=(200, 200, 206, int(255 * a)))
        _karta_reklamy(d, x0 + 20, y0 + 230, x1 - 20, y0 + 500, a, True, akc)
        # odbicie "znowu ten sam" - trzy male kopie produktu
        for i in range(3):
            q = wej(tt, 0.6 + i * 0.3, 0.3)
            if q > 0:
                xx = x0 + 60 + i * ((x1 - x0 - 120) / 2)
                d.rounded_rectangle([xx - 34, y0 + 540, xx + 34, y0 + 600], radius=8, fill=akc + (int(200 * q),))
        im2.alpha_composite(nak)
    telefon(im, CX, dol + 470, 0.95, 1.0, ekran, t)


def scena_sciezka(im, t, dl, p, kt):
    """Sciezka zakupu: szuka -> porownuje -> kupuje; klient na poczatku, znak zapytania."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    etapy = ["SZUKA", "PORÓWNUJE", "KUPUJE"]
    ys = [460, 680, 900]
    for i, (et, y) in enumerate(zip(etapy, ys)):
        pi_ = wej(t, 0.1 + i * 0.2, 0.3)
        d.rounded_rectangle([CX - 230, y - 60, CX + 230, y + 60], radius=60,
                            fill=((akc if i == 0 else (70, 72, 82)) + (int(235 * pi_),)))
        f = f_anton(52)
        d.text((CX - szer(d, et, f) / 2, y - 36), et, font=f, fill=((CIEMNY if i == 0 else BIEL) + (int(255 * pi_),)))
        if i < 2:
            strzalka(d, (CX, y + 64), (CX, ys[i + 1] - 64), (150, 152, 162), pi_, grub=7)
    po = pop(t, 0.6, 0.4)
    if po > 0:
        czlowiek(d, CX - 330, 460, 60 * po, BIEL, 1.0)
        f = f_anton(int(80 * po) or 1)
        d.text((CX - 330 + 40, 340), "?", font=f, fill=akc + (255,))
    im.alpha_composite(nak)


def scena_dwie_reklamy(im, t, dl, p, kt):
    """Wynik: zwykla reklama marki wygrala z reklama ogladanego produktu."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    f0 = f_anton(54)
    tx = p.get("tytul", "KTÓRA SPRZEDAŁA LEPIEJ?")
    fb = dopasuj(d, tx, X1 - X0, 56, 36, f_anton)
    d.text((CX - szer(d, tx, fb) / 2, 300), tx, font=fb, fill=BIEL + (int(255 * a),))
    fs = f_inter(30, False)
    pt = p.get("podtytul", "")
    d.text((CX - szer(d, pt, fs) / 2, 380), pt, font=fs, fill=SZARY + (int(255 * a),))
    for j, (cx, prod, et) in enumerate(((CX - 200, False, "reklama marki"), (CX + 200, True, "oglądany produkt"))):
        pj = wej(t, 0.2 + j * 0.25, 0.4)
        _karta_reklamy(d, cx - 170, 470, cx + 170, 820, pj, prod, akc)
        f = f_inter(32)
        d.text((cx - szer(d, et, f) / 2, 840), et, font=f, fill=SZARY + (int(255 * pj),))
    tw = kt["czas_slowa"](p.get("wynik_od", "lepiej")) - kt["od"] - 0.1
    pw = pop(t, tw, 0.45)
    if pw > 0:
        ptaszek(d, CX - 200, 990, 60 * pw)
        krzyzyk(d, CX + 200, 990, 50, 1.0, min(1.0, pw))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- b3: odpowiadanie na opinie

def _gwiazdki(d, x, y, n, r, a, kol=ZOLTY):
    for i in range(5):
        cx = x + i * (r * 2.3)
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(ang), y + rr * math.sin(ang)))
        d.polygon(pts, fill=(kol if i < n else (90, 92, 104)) + (int(255 * a),))


def _opinia(d, x0, y0, x1, n, a, odp=0.0, akc=ZOLTY):
    d.rounded_rectangle([x0, y0, x1, y0 + 150], radius=16, fill=(52, 52, 62, int(255 * a)))
    d.ellipse([x0 + 20, y0 + 20, x0 + 70, y0 + 70], fill=(120, 122, 134, int(255 * a)))
    _gwiazdki(d, x0 + 100, y0 + 44, n, 16, a)
    d.rounded_rectangle([x0 + 24, y0 + 92, x1 - 60, y0 + 108], radius=8, fill=(170, 172, 182, int(255 * a)))
    d.rounded_rectangle([x0 + 24, y0 + 118, x1 - 160, y0 + 132], radius=7, fill=(120, 122, 134, int(255 * a)))
    if odp > 0:
        d.rounded_rectangle([x0 + 80, y0 + 165, x1, y0 + 245], radius=16, fill=akc + (int(235 * odp),))
        f = f_inter(26)
        d.text((x0 + 104, y0 + 175), "Odpowiedź właściciela", font=f, fill=CIEMNY + (int(255 * odp),))
        d.rounded_rectangle([x0 + 104, y0 + 212, x1 - 60, y0 + 226], radius=7, fill=(30, 30, 36, int(160 * odp)))


def scena_pytanie_opinie(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, x1 = X0 + 20, X1 - 20
    y = dol + 80
    _opinia(d, x0, y, x1, 2, 1.0, odp=wej(t, 0.8, 0.4), akc=akc)
    _opinia(d, x0, y + 290, x1, 5, wej(t, 0.2, 0.3), akc=akc)
    im.alpha_composite(nak)


def scena_nastepni(im, t, dl, p, kt):
    """Nastepny klient widzi, ze wlasciciel czyta - pisze ostrozniej."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    x0, x1 = X0 + 20, X1 - 20
    _opinia(d, x0, 330, x1, 3, a, odp=1.0, akc=akc)
    po = pop(t, 0.3, 0.4)
    if po > 0:
        ik_oko(d, CX - 220, 700, 60 * po, akc, 1.0)
        czlowiek(d, CX - 220, 860, 70 * po, BIEL, 1.0)
        f = f_anton(48)
        pigulka(d, CX + 120, 760, "KTOŚ TO CZYTA", f, akc + (240,), CIEMNY + (255,))
    if t > 1.2:
        q = wej(t, 1.2, 0.4)
        _opinia(d, x0, 980 - 40 * (1 - q), x1, 4, q, akc=akc)
    im.alpha_composite(nak)


s6.SCENY.update({
    "dwa_wzrosty": scena_dwa_wzrosty,
    "pytanie_mail": scena_pytanie_mail, "do_jednej": scena_do_jednej,
    "pytanie_retarget": scena_pytanie_retarget, "sciezka": scena_sciezka, "dwie_reklamy": scena_dwie_reklamy,
    "pytanie_opinie": scena_pytanie_opinie, "nastepni": scena_nastepni,
})


def scena_slupki_slowa(im, t, dl, p, kt):
    """Jak slupki2, ale kazdy slupek rosnie na swoim slowie lektora (p['starty'])."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    if tl:
        fb = dopasuj(d, tl, X1 - X0, 64, 36, f_anton)
        d.text((CX - szer(d, tl, fb) / 2, 300), tl, font=fb, fill=BIEL + (int(255 * a),))
    if p.get("podtytul"):
        fs = f_inter(30, False)
        d.text((CX - szer(d, p["podtytul"], fs) / 2, 390), p["podtytul"], font=fs, fill=SZARY + (int(255 * a),))
    kolory = [tuple(x) for x in p.get("kolory", [ZIELONY, (110, 112, 124)])]
    wart, etyk = p["wartosci"], p["etykiety"]
    mx = max(wart)
    for i in range(2):
        t0 = kt["czas_slowa"](p["starty"][i]) - kt["od"] - 0.15
        # pojedynczy slupek: rysowany recznie, ta sama geometria co dwa_slupki
        szer_s, y_dol, wys_max = 220, 1150, 520
        x = [CX - 170, CX + 170][i]
        q = wej(t, t0, 0.8)
        h = wys_max * wart[i] / mx * q
        d.rounded_rectangle([x - szer_s / 2, y_dol - max(h, 6), x + szer_s / 2, y_dol], radius=18,
                            fill=kolory[i] + (int(255 * max(a * 0.35, min(1.0, q * 3))),))
        if q > 0.05:
            v = wart[i] * q
            tx = (f"{v:.1f}".replace(".", ",") if wart[i] != int(wart[i]) else f"{int(round(v))}") + p.get("jedn", "%")
            fb = f_anton(96)
            d.text((x - szer(d, tx, fb) / 2, y_dol - h - 120), tx, font=fb, fill=BIEL + (255,))
        fe = dopasuj(d, etyk[i], 330, 36, 24)
        d.text((x - szer(d, etyk[i], fe) / 2, y_dol + 20), etyk[i], font=fe, fill=SZARY + (int(255 * a),))
    im.alpha_composite(nak)


s6.SCENY["slupki_slowa"] = scena_slupki_slowa


# ---------------------------------------------------------------- c1: rabat na start vs zadatek

def _metka_ceny(d, cx, cy, tekst, kol, a, s=1.0):
    w, h = 230 * s, 120 * s
    d.polygon([(cx - w / 2, cy - h / 2), (cx + w / 2 - 40 * s, cy - h / 2), (cx + w / 2, cy), (cx + w / 2 - 40 * s, cy + h / 2),
               (cx - w / 2, cy + h / 2)], fill=kol + (int(255 * a),))
    f = f_anton(int(62 * s))
    d.text((cx - 20 * s - szer(d, tekst, f) / 2, cy - f.size * 0.62), tekst, font=f, fill=CIEMNY + (int(255 * a),))


def scena_pytanie_rabat(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    # karnet z metka rabatu, ktora wpada z gory
    x0, y0, x1, y1 = CX - 300, dol + 120, CX + 300, dol + 470
    d.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=(52, 52, 62, 255), outline=(90, 92, 104, 255), width=3)
    for i in range(3):
        d.rounded_rectangle([x0 + 40, y0 + 60 + i * 60, x1 - 160 - i * 40, y0 + 84 + i * 60], radius=10, fill=(150, 152, 162, 255))
    d.line([x1 - 120, y0 + 20, x1 - 120, y1 - 20], fill=(30, 30, 36, 255), width=4)
    po = pop(t, 0.3, 0.45)
    if po > 0:
        _metka_ceny(d, x1 - 40, y0 + 20, "RABAT", akc, 1.0, s=po)
    im.alpha_composite(nak)


def scena_mniej_zal(im, t, dl, p, kt):
    """Pelna cena -> idzie; rabat -> zostaje w domu."""
    akc = kt["akcent"]
    nak, d = warstwa()
    for j, (cx, tag, kol, idzie) in enumerate(((CX - 200, "PEŁNA", ZIELONY, True), (CX + 200, "RABAT", akc, False))):
        pj = wej(t, 0.1 + j * 0.35, 0.4)
        _metka_ceny(d, cx, 360, tag, kol, pj, s=0.85)
        czlowiek(d, cx, 600, 80, BIEL, pj)
        if idzie:
            strzalka(d, (cx, 720), (cx, 880), ZIELONY, pj, grub=9)
            d.rectangle([cx - 70, 900, cx + 70, 1010], fill=(90, 92, 104, int(255 * pj)))
            d.rectangle([cx - 24, 940, cx + 24, 1010], fill=(30, 30, 36, int(255 * pj)))
            f = f_inter(30)
            d.text((cx - szer(d, "przychodzi", f) / 2, 1030), "przychodzi", font=f, fill=BIEL + (int(255 * pj),))
        else:
            # domek
            d.polygon([(cx - 90, 920), (cx, 840), (cx + 90, 920)], fill=(90, 92, 104, int(255 * pj)))
            d.rectangle([cx - 70, 920, cx + 70, 1010], fill=(90, 92, 104, int(255 * pj)))
            f = f_inter(30)
            d.text((cx - szer(d, "zostaje w domu", f) / 2, 1030), "zostaje w domu", font=f, fill=BIEL + (int(255 * pj),))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- c2: klient z polecenia

def scena_pytanie_polecenie(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    y = dol + 300
    for j, (cx, et, kol) in enumerate(((CX - 200, "z polecenia", akc), (CX + 200, "z reklamy", (150, 152, 162)))):
        czlowiek(d, cx, y, 100, kol, 1.0)
        f = f_inter(34)
        d.text((cx - szer(d, et, f) / 2, y + 110), et, font=f, fill=BIEL + (255,))
    po = pop(t, 0.4, 0.4)
    if po > 0:
        f = f_anton(int(120 * po) or 1)
        d.text((CX - szer(d, "?", f) / 2, y - 60), "?", font=f, fill=akc + (255,))
    im.alpha_composite(nak)


def scena_dopasowanie(im, t, dl, p, kt):
    """Znajomy laczy do firmy kogos, kto pasuje - klient zostaje dluzej."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, CX - 250, 520, 80, ZIELONY, a)
    f = f_inter(28)
    d.text((CX - 250 - szer(d, "znajomy", f) / 2, 620), "znajomy", font=f, fill=BIEL + (int(255 * a),))
    p1 = wej(t, 0.3, 0.5)
    strzalka(d, (CX - 170, 520), (CX - 40, 520), akc, a, grub=8, postep=p1)
    if p1 > 0.6:
        czlowiek(d, CX + 30, 520, 80, akc, 1.0)
        d.text((CX + 30 - szer(d, "nowy klient", f) / 2, 620), "nowy klient", font=f, fill=BIEL + (255,))
    p2 = wej(t, 0.9, 0.5)
    strzalka(d, (CX + 110, 520), (CX + 230, 520), akc, a, grub=8, postep=p2)
    if p2 > 0.6:
        d.rectangle([CX + 240, 460, CX + 380, 580], fill=(90, 92, 104, 255))
        for i in range(4):
            k = (CZERW if i % 2 == 0 else BIEL) + (255,)
            d.rectangle([CX + 232 + i * 39, 430, CX + 232 + (i + 1) * 39, 460], fill=k)
    if t > 1.6:
        f2 = f_anton(48)
        pigulka(d, CX, 760, "PASUJE = ZOSTAJE DŁUŻEJ", f2, akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- c3: chatbot udajacy czlowieka

def _dymek_czat(d, x0, y, x1, a, kol, prawy=False):
    d.rounded_rectangle([x0, y, x1, y + 70], radius=22, fill=kol + (int(255 * a),))
    d.rounded_rectangle([x0 + 24, y + 24, x1 - 60, y + 44], radius=8, fill=(30, 30, 36, int(120 * a)))


def scena_pytanie_bot(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, y0, x1, y1 = X0 + 20, dol + 70, X1 - 20, dol + 640
    okno_przegladarki(d, x0, y0, x1, y1, 1.0)
    # naglowek czatu: awatar z buzia i "imie"
    cx, cy = x0 + 90, y0 + 140
    d.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=akc + (255,))
    d.ellipse([cx - 18, cy - 12, cx - 8, cy - 2], fill=CIEMNY + (255,))
    d.ellipse([cx + 8, cy - 12, cx + 18, cy - 2], fill=CIEMNY + (255,))
    d.arc([cx - 20, cy - 4, cx + 20, cy + 22], 20, 160, fill=CIEMNY + (255,), width=5)
    f = f_inter(36)
    d.text((cx + 70, cy - 24), "Ola, konsultantka", font=f, fill=BIEL + (255,))
    _dymek_czat(d, x0 + 30, y0 + 230, x1 - 160, wej(t, 0.3, 0.3), (90, 92, 104))
    _dymek_czat(d, x0 + 160, y0 + 330, x1 - 30, wej(t, 0.8, 0.3), akc)
    po = pop(t, 1.3, 0.4)
    if po > 0:
        f2 = f_anton(int(90 * po) or 1)
        d.text((CX - szer(d, "BOT?", f2) / 2, y0 + 440), "BOT?", font=f2, fill=CZERW + (255,))
    im.alpha_composite(nak)


def scena_oczekiwania(im, t, dl, p, kt):
    """Zdenerwowany klient: od 'czlowieka' oczekuje wiecej - zawod wiekszy."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, CX, 430, 90, CZERW, a)
    f = f_inter(30)
    d.text((CX - szer(d, "zdenerwowany klient", f) / 2, 530), "zdenerwowany klient", font=f, fill=BIEL + (int(255 * a),))
    f2 = f_anton(44)
    for j, (et, ocz) in enumerate((("BOT", 0.35), ("BOT „CZŁOWIEK”", 0.9))):
        y = 660 + j * 170
        pj = wej(t, 0.4 + j * 0.4, 0.5)
        d.text((X0 + 20, y), et, font=f2, fill=BIEL + (int(255 * pj),))
        d.rounded_rectangle([X0 + 20, y + 64, X1 - 20, y + 104], radius=20, fill=(60, 62, 72, int(255 * pj)))
        d.rounded_rectangle([X0 + 20, y + 64, X0 + 20 + (X1 - X0 - 40) * ocz * pj, y + 104], radius=20,
                            fill=((CZERW if j == 1 else (150, 152, 162)) + (int(255 * pj),)))
    if t > 1.4:
        pigulka(d, CX, 1010, "WIĘKSZE OCZEKIWANIA = WIĘKSZY ZAWÓD", f_anton(40), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_rabat": scena_pytanie_rabat, "mniej_zal": scena_mniej_zal,
    "pytanie_polecenie": scena_pytanie_polecenie, "dopasowanie": scena_dopasowanie,
    "pytanie_bot": scena_pytanie_bot, "oczekiwania": scena_oczekiwania,
})


# ---------------------------------------------------------------- d1: jedna zla opinia (19.11)

def scena_pytanie_jedna(im, t, dl, p, kt):
    """Karta produktu z dobrymi opiniami; od startu widac jedna zla opinie na czerwono."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, x1 = X0 + 20, X1 - 20
    y = dol + 70
    _opinia(d, x0, y, x1, 5, 1.0, akc=akc)
    _opinia(d, x0, y + 175, x1, 5, 1.0, akc=akc)
    q = 0.6 + 0.4 * wej(t, 0.3, 0.4)
    d.rounded_rectangle([x0 - 8, y + 342, x1 + 8, y + 508], radius=20, outline=CZERW + (int(255 * q),), width=6)
    _opinia(d, x0, y + 350, x1, 1, 1.0, akc=akc)
    im.alpha_composite(nak)


def scena_szuka_powodu(im, t, dl, p, kt):
    """Klient czyta opinie i szuka powodu, zeby nie kupic - zla opinia mu go daje."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, CX - 260, 470, 80, BIEL, a)
    ik_oko(d, CX - 260, 640, 46, akc, a)
    x0, x1 = CX - 120, X1 - 20
    for i, n in enumerate((5, 4, 1)):
        pj = wej(t, 0.2 + i * 0.3, 0.3)
        yy = 330 + i * 190
        d.rounded_rectangle([x0, yy, x1, yy + 150], radius=16, fill=(52, 52, 62, int(255 * pj)),
                            outline=(CZERW + (int(255 * pj),)) if n == 1 else None, width=6 if n == 1 else 0)
        _gwiazdki(d, x0 + 30, yy + 44, n, 16, pj)
        d.rounded_rectangle([x0 + 24, yy + 92, x1 - 60, yy + 108], radius=8, fill=(170, 172, 182, int(255 * pj)))
    f = f_anton(44)
    if t > 0.3:
        pigulka(d, CX, 950, "SZUKA POWODU, ŻEBY NIE KUPIĆ", f, (60, 62, 72, 240), BIEL + (255,))
    t1 = kt["czas_slowa"]("negatywna") - kt["od"] - 0.1
    if t > t1:
        pigulka(d, CX, 1060, "JEDNA ZŁA OPINIA = POWÓD", f, CZERW + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_duza_liczba(im, t, dl, p, kt):
    """Duza liczba liczona od zera na slowie lektora (p['start']), z tytulem i podpisem."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    fb = dopasuj(d, tl, X1 - X0, 60, 36, f_anton)
    d.text((CX - szer(d, tl, fb) / 2, 330), tl, font=fb, fill=BIEL + (int(255 * a),))
    t0 = kt["czas_slowa"](p["start"]) - kt["od"] - 0.15
    q = wej(t, t0, 0.8)
    kol = tuple(p.get("kolor", CZERW))
    y_l = 520
    if p.get("opinia"):
        # zla opinia widoczna od wejscia sceny, zanim padnie liczba (bez pustego kadru)
        _opinia(d, X0 + 60, 430, X1 - 60, 1, a)
        d.rounded_rectangle([X0 + 52, 422, X1 - 52, 588], radius=20, outline=CZERW + (int(255 * a),), width=6)
        y_l = 640
    if p.get("metki"):
        for j, m in enumerate(p["metki"]):
            _metka_ceny(d, CX - 180 + j * 360, 500, m, (150, 152, 162) if j == 0 else kt["akcent"], a, s=0.9)
        y_l = 640
    if p.get("ikony"):
        czlowiek(d, CX - 160, 500, 70, (110, 170, 240), a)
        czlowiek(d, CX + 160, 500, 70, (240, 140, 190), a)
        y_l = 640
    if q > 0:
        v = p["wartosc"] * q
        num = f"{int(round(v))}" if float(p["wartosc"]).is_integer() else f"{v:.1f}".replace(".", ",")
        tx = p.get("znak", "") + num + "%"
        f = f_anton(int(230 * (0.9 + 0.1 * pop(t, t0, 0.4))))
        d.text((CX - szer(d, tx, f) / 2, y_l), tx, font=f, fill=kol + (255,))
        fs = f_inter(38)
        for j, ln in enumerate(p.get("podpis", [])):
            d.text((CX - szer(d, ln, fs) / 2, y_l + 340 + j * 56), ln, font=fs, fill=BIEL + (int(255 * min(1, q * 2)),))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- d2: mailing z rabatem

def _koperta(d, cx, cy, w, a, otw=0.0, kol=(150, 152, 162)):
    h = w * 0.62
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d.rectangle([x0, y0, x1, y1], fill=kol + (int(255 * a),))
    gy = y0 - (h * 0.55) * otw + (h * 0.55) * (1 - otw)
    d.polygon([(x0, y0), (cx, gy), (x1, y0)], fill=(110, 112, 124, int(255 * a)))
    d.line([(x0, y1), (cx, cy + h * 0.05), (x1, y1)], fill=(110, 112, 124, int(255 * a)), width=4)


def scena_pytanie_kod(im, t, dl, p, kt):
    """Otwarta koperta, z ktorej od startu wystaje kupon z kodem rabatowym."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    w = 520
    h = w * 0.62
    cy = dol + 470
    x0, y0, x1, y1 = CX - w / 2, cy - h / 2, CX + w / 2, cy + h / 2
    d.polygon([(x0, y0), (CX, y0 - h * 0.55), (x1, y0)], fill=(110, 112, 124, 255))
    wy = 140 * wej(t, 0.2, 0.6)
    d.rounded_rectangle([CX - 210, y0 - 40 - wy, CX + 210, y0 + 150 - wy], radius=16, fill=akc + (255,))
    f = f_anton(56)
    d.text((CX - szer(d, "KOD RABATOWY", f) / 2, y0 - 12 - wy), "KOD RABATOWY", font=f, fill=CIEMNY + (255,))
    d.rectangle([x0, y0 + 40, x1, y1], fill=(150, 152, 162, 255))
    d.line([(x0, y1), (CX, cy + h * 0.1), (x1, y1)], fill=(110, 112, 124, 255), width=4)
    im.alpha_composite(nak)


def scena_przypomina(im, t, dl, p, kt):
    """Mail przypomina o firmie - klient kupuje tez rzeczy bez kodu."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _koperta(d, CX - 300, 470, 200, a)
    p1 = wej(t, 0.3, 0.5)
    strzalka(d, (CX - 180, 470), (CX - 60, 470), akc, a, grub=8, postep=p1)
    if p1 > 0.5:
        czlowiek(d, CX, 470, 80, BIEL, 1.0)
        f = f_inter(28)
        d.text((CX - szer(d, "pamięta o firmie", f) / 2, 570), "pamięta o firmie", font=f, fill=BIEL + (255,))
    t1 = kt["czas_slowa"]("kupuje") - kt["od"] - 0.1
    p2 = wej(t, t1, 0.5)
    strzalka(d, (CX + 90, 470), (CX + 200, 470), akc, a, grub=8, postep=p2)
    if p2 > 0.4:
        for i in range(3):
            pk = pop(t, t1 + 0.2 + i * 0.15, 0.3)
            if pk > 0:
                x, y = CX + 270, 380 + i * 90
                d.rounded_rectangle([x - 50 * pk, y - 32 * pk, x + 50 * pk, y + 32 * pk], radius=10, fill=ZIELONY + (255,))
        pigulka(d, CX, 800, "KUPUJE TEŻ BEZ KODU", f_anton(48), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_podzial(im, t, dl, p, kt):
    """+37% wydatkow na 1. slowie, potem pasek dzieli sie na 90% bez kodu / 10% z kodem."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    fb = f_anton(56)
    d.text((CX - szer(d, p["tytul"], fb) / 2, 320), p["tytul"], font=fb, fill=BIEL + (int(255 * a),))
    t0 = kt["czas_slowa"](p["start1"]) - kt["od"] - 0.15
    q = wej(t, t0, 0.7)
    if q < 1 and p.get("koperty", True):
        # koperta z ofertami trzyma kadr, zanim padnie liczba (bez pustego tla)
        for j in range(3):
            _koperta(d, CX - 220 + j * 220, 560 + (j % 2) * 40, 170, a * (1 - q))
    if q < 1 and p.get("ludzie"):
        for j in range(12):
            czlowiek(d, CX - 375 + (j % 6) * 150, 500 + (j // 6) * 170, 46, (170, 172, 182), a * (1 - q))
    if q > 0:
        tx = f"+{int(round(p['liczba1'] * q))}%"
        f = f_anton(190)
        d.text((CX - szer(d, tx, f) / 2, 420), tx, font=f, fill=ZIELONY + (255,))
        fs = f_inter(36)
        d.text((CX - szer(d, p["podpis1"], fs) / 2, 650), p["podpis1"], font=fs, fill=BIEL + (int(255 * q),))
    t1 = kt["czas_slowa"](p["start2"]) - kt["od"] - 0.15
    q2 = wej(t, t1, 0.8)
    x0, x1, y0 = X0 + 20, X1 - 20, 800
    if q2 > 0:
        d.rounded_rectangle([x0, y0, x1, y0 + 110], radius=24, fill=(60, 62, 72, 255))
        pr = p.get("proc2", 90)
        xs = x0 + (x1 - x0) * pr / 100 * q2
        d.rounded_rectangle([x0, y0, xs, y0 + 110], radius=24, fill=akc + (255,))
        f = f_anton(64)
        tx = f"{int(round(pr * q2))}% " + p.get("et2", "BEZ KODU")
        d.text((x0 + 30, y0 + 18), tx, font=f, fill=CIEMNY + (255,))
        fs = f_inter(30)
        rs = p.get("reszta", "10% z kodem")
        d.text((x1 - szer(d, rs, fs), y0 + 130), rs, font=fs, fill=SZARY + (int(255 * q2),))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- d3: darmowa dostawa

def _paczka(d, cx, cy, s, a, kol=(196, 160, 110)):
    d.rectangle([cx - 50 * s, cy - 40 * s, cx + 50 * s, cy + 40 * s], fill=kol + (int(255 * a),))
    d.line([cx, cy - 40 * s, cx, cy + 40 * s], fill=(150, 120, 80, int(255 * a)), width=max(1, int(6 * s)))


def _auto(d, cx, cy, a, kol=BIEL, s=1.0):
    d.rounded_rectangle([cx - 150 * s, cy - 80 * s, cx + 40 * s, cy + 40 * s], radius=12, fill=kol + (int(255 * a),))
    d.rounded_rectangle([cx + 40 * s, cy - 40 * s, cx + 140 * s, cy + 40 * s], radius=12, fill=kol + (int(255 * a),))
    for x in (cx - 90 * s, cx + 90 * s):
        d.ellipse([x - 32 * s, cy + 16 * s, x + 32 * s, cy + 80 * s], fill=(30, 30, 36, int(255 * a)))


def scena_pytanie_dostawa(im, t, dl, p, kt):
    """Bus dostawczy jedzie z metka 0 ZL od pierwszej klatki."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cx = CX - 60 + 80 * min(1.0, t / 2.5)
    cy = dol + 380
    _auto(d, cx, cy, 1.0, s=1.8)
    f = f_anton(84)
    pigulka(d, cx - 100, cy - 90, "0 ZŁ", f, akc + (255,), CIEMNY + (255,))
    for i in range(3):
        d.line([cx - 360 - i * 50, cy - 80 + i * 50, cx - 290 - i * 50, cy - 80 + i * 50], fill=SZARY + (180,), width=6)
    im.alpha_composite(nak)


def scena_zwroty(im, t, dl, p, kt):
    """Paczki ida do klienta, a czesc wraca - zwroty kosztuja."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _auto(d, CX - 250, 470, a, kol=(150, 152, 162))
    czlowiek(d, CX + 280, 450, 80, BIEL, a)
    for i in range(3):
        q = (t * 0.7 + i * 0.34) % 1.0
        _paczka(d, CX - 120 + 300 * q, 380, 0.7, a)
    t1 = kt["czas_slowa"]("oddaje") - kt["od"] - 0.1
    if t > t1:
        for i in range(2):
            q = ((t - t1) * 0.7 + i * 0.5) % 1.0
            _paczka(d, CX + 180 - 300 * q, 600, 0.7, 1.0, kol=CZERW)
        strzalka(d, (CX + 180, 690), (CX - 120, 690), CZERW, 1.0, grub=8)
    t2 = kt["czas_slowa"]("kosztują") - kt["od"] - 0.15
    if t > t2:
        pigulka(d, CX, 880, "ZWROT = KOSZT DLA SKLEPU", f_anton(48), CZERW + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_dwa_wskazniki(im, t, dl, p, kt):
    """Dwie liczby ze strzalkami gora/dol, kazda liczona na swoim slowie."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    fb = dopasuj(d, tl, X1 - X0, 56, 36, f_anton)
    d.text((CX - szer(d, tl, fb) / 2, 320), tl, font=fb, fill=BIEL + (int(255 * a),))
    if p.get("metka_bf"):
        t_pierw = kt["czas_slowa"](p["pozycje"][0]["od"]) - kt["od"] - 0.15
        za = a * (1 - wej(t, t_pierw, 0.4))
        if za > 0:
            _metka_bf(d, CX, 640, za, kt["akcent"], s=1.4)
    if p.get("auto"):
        # bus z paczkami trzyma kadr, zanim padnie pierwsza liczba
        t_pierw = kt["czas_slowa"](p["pozycje"][0]["od"]) - kt["od"] - 0.15
        za = a * (1 - wej(t, t_pierw, 0.4))
        if za > 0:
            _auto(d, CX - 60 + 60 * min(1.0, t / 3), 640, za, s=1.5)
            pigulka(d, CX - 140, 560, "0 ZŁ", f_anton(64), kt["akcent"] + (int(255 * za),), CIEMNY + (int(255 * za),))
    if p.get("twarze"):
        # siatka zdjec (z twarza / bez) trzyma kadr, zanim padnie pierwsza liczba
        t_pierw = kt["czas_slowa"](p["pozycje"][0]["od"]) - kt["od"] - 0.15
        za = a * (1 - wej(t, t_pierw, 0.4))
        if za > 0:
            for k in range(6):
                x, y = X0 + 70 + (k % 3) * 300, 470 + (k // 3) * 300
                _zdjecie(d, x, y, 250, za, k % 2 == 0, kt["akcent"])
    for i, poz in enumerate(p["pozycje"]):
        t0 = kt["czas_slowa"](poz["od"]) - kt["od"] - 0.15
        q = wej(t, t0, 0.7)
        if q <= 0:
            continue
        y = 450 + i * 330
        kol = tuple(poz["kolor"]) if poz.get("kolor") else (ZIELONY if poz["kierunek"] > 0 else CZERW)
        v = poz["wartosc"] * q
        num = f"{int(round(v))}" if float(poz["wartosc"]).is_integer() else f"{v:.1f}".replace(".", ",")
        tx = ("+" if poz["kierunek"] > 0 else "-") + num + "%"
        f = f_anton(150)
        d.text((CX - 40 - szer(d, tx, f) / 2, y), tx, font=f, fill=kol + (255,))
        ax = CX + szer(d, tx, f) / 2 + 20
        if poz["kierunek"] > 0:
            strzalka(d, (ax, y + 170), (ax, y + 30), kol, q, grub=12)
        else:
            strzalka(d, (ax, y + 30), (ax, y + 170), kol, q, grub=12)
        fs = f_inter(40)
        d.text((CX - szer(d, poz["podpis"], fs) / 2, y + 200), poz["podpis"], font=fs, fill=BIEL + (int(255 * q),))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_jedna": scena_pytanie_jedna, "szuka_powodu": scena_szuka_powodu, "duza_liczba": scena_duza_liczba,
    "pytanie_kod": scena_pytanie_kod, "przypomina": scena_przypomina, "podzial": scena_podzial,
    "pytanie_dostawa": scena_pytanie_dostawa, "zwroty": scena_zwroty, "dwa_wskazniki": scena_dwa_wskazniki,
})


# ---------------------------------------------------------------- e1: cena z dziewiatka (20.11)

def scena_pytanie_dziewiatka(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 330
    s = 1.6
    w, h = 230 * s, 120 * s
    d.polygon([(CX - w / 2, cy - h / 2), (CX + w / 2 - 40 * s, cy - h / 2), (CX + w / 2, cy), (CX + w / 2 - 40 * s, cy + h / 2),
               (CX - w / 2, cy + h / 2)], fill=BIEL + (255,))
    f = f_anton(int(62 * s * 1.3))
    x = CX - 20 * s - szer(d, "39", f) / 2
    d.text((x, cy - f.size * 0.62), "3", font=f, fill=CIEMNY + (255,))
    pq = 0.6 + 0.4 * wej(t, 0.3, 0.4)
    d.text((x + szer(d, "3", f), cy - f.size * 0.62), "9", font=f, fill=akc + (int(255 * pq),))
    im.alpha_composite(nak)


def scena_okazja(im, t, dl, p, kt):
    """Dwie metki 35 i 39 - dziewiatka wyglada jak okazja, choc drozsza."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _metka_ceny(d, CX - 190, 470, "35", (150, 152, 162), a, s=1.0)
    p2 = pop(t, 0.3, 0.45)
    if p2 > 0:
        _metka_ceny(d, CX + 190, 470, "39", akc, 1.0, s=p2)
    t1 = kt["czas_slowa"]("okazja") - kt["od"] - 0.1
    if t > t1:
        pigulka(d, CX + 190, 610, "OKAZJA?", f_anton(52), ZIELONY + (240,), CIEMNY + (255,))
    t2 = kt["czas_slowa"]("wyższa") - kt["od"] - 0.15
    if t > t2:
        pigulka(d, CX, 800, "WYŻSZA CENA, A WYGLĄDA NA OKAZJĘ", f_anton(42), (60, 62, 72, 240), BIEL + (255,))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- e2: dopasowanie + duzy format

def scena_pytanie_format(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, y0, x1, y1 = X0 + 20, dol + 70, X1 - 20, dol + 640
    okno_przegladarki(d, x0, y0, x1, y1, 1.0)
    for i in range(6):
        d.rounded_rectangle([x0 + 30, y0 + 100 + i * 70, x1 - 30 - (i % 2) * 80, y0 + 124 + i * 70], radius=8, fill=(150, 152, 162, 255))
    q = wej(t, 0.2, 0.5)
    yy = y1 - 30 - (y1 - y0 - 110) * 0.55 * q
    d.rounded_rectangle([x0 + 10, yy, x1 - 10, y1 - 10], radius=18, fill=akc + (255,))
    cx, cy = CX, (yy + y1) / 2
    for r in (60, 36, 12):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CIEMNY + (255,), width=6)
    d.line([cx - 80, cy, cx + 80, cy], fill=CIEMNY + (255,), width=4)
    d.line([cx, cy - 80, cx, cy + 80], fill=CIEMNY + (255,), width=4)
    im.alpha_composite(nak)


def scena_sledzony(im, t, dl, p, kt):
    """Klient pod celownikiem czuje sie sledzony i sie broni."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, CX, 520, 100, BIEL, a)
    r = 170 - 30 * min(1, t / 1.0)
    d.ellipse([CX - r, 520 - r, CX + r, 520 + r], outline=CZERW + (int(255 * a),), width=6)
    d.line([CX - r - 40, 520, CX + r + 40, 520], fill=CZERW + (int(200 * a),), width=4)
    d.line([CX, 520 - r - 40, CX, 520 + r + 40], fill=CZERW + (int(200 * a),), width=4)
    t1 = kt["czas_slowa"]("śledzony") - kt["od"] - 0.1
    if t > t1:
        pigulka(d, CX, 780, "CZUJE SIĘ ŚLEDZONY", f_anton(50), CZERW + (240,), CIEMNY + (255,))
    t2 = kt["czas_slowa"]("bronić") - kt["od"] - 0.15
    if t > t2:
        # tarcza
        sx, sy = CX + 230, 470
        d.polygon([(sx - 60, sy - 70), (sx + 60, sy - 70), (sx + 60, sy + 10), (sx, sy + 80), (sx - 60, sy + 10)], fill=akc + (255,))
        pigulka(d, CX, 890, "I ZACZYNA SIĘ BRONIĆ", f_anton(46), (60, 62, 72, 240), BIEL + (255,))
    im.alpha_composite(nak)


def scena_trzy_paski(im, t, dl, p, kt):
    """Poziome paski: kazdy osobno rosnie, razem slabiej - kazdy na swoim slowie."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    fb = dopasuj(d, tl, X1 - X0, 56, 36, f_anton)
    d.text((CX - szer(d, tl, fb) / 2, 320), tl, font=fb, fill=BIEL + (int(255 * a),))
    for i, poz in enumerate(p["pozycje"]):
        t0 = kt["czas_slowa"](poz["od"]) - kt["od"] - 0.15 + poz.get("opozn", 0)
        q = wej(t, t0, 0.7)
        y = 440 + i * 200
        fs = f_inter(36)
        d.text((X0 + 20, y), poz["etykieta"], font=fs, fill=BIEL + (int(255 * max(a * 0.5, min(1, q * 2))),))
        d.rounded_rectangle([X0 + 20, y + 56, X1 - 20, y + 116], radius=26, fill=(60, 62, 72, int(255 * a)))
        if q > 0:
            kol = tuple(poz.get("kolor", ZIELONY))
            d.rounded_rectangle([X0 + 20, y + 56, X0 + 20 + (X1 - X0 - 40) * poz["dl"] * q, y + 116], radius=26, fill=kol + (255,))
            f = f_anton(48)
            d.text((X1 - 30 - szer(d, poz["opis"], f), y - 6), poz["opis"], font=f, fill=kol + (int(255 * q),))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- e3: algorytm szuka najtanszych

def scena_pytanie_algorytm(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 330
    for j, kol in enumerate(((110, 170, 240), (240, 140, 190), (110, 170, 240), (240, 140, 190))):
        czlowiek(d, CX - 300 + j * 200, cy + 60, 60, kol, 1.0)
    r = 120
    cx = CX - 200 + 400 * (0.5 + 0.5 * math.sin(t * 1.6))
    d.ellipse([cx - r, cy + 60 - r, cx + r, cy + 60 + r], outline=akc + (255,), width=7)
    d.line([cx - r - 30, cy + 60, cx + r + 30, cy + 60], fill=akc + (220,), width=4)
    d.line([cx, cy + 60 - r - 30, cx, cy + 60 + r + 30], fill=akc + (220,), width=4)
    im.alpha_composite(nak)


def scena_najtansze(im, t, dl, p, kt):
    """Algorytm wybiera tansze wyswietlenia: stos monet mniejszy = czesciej pokazuje."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    f = f_anton(56)
    pigulka(d, CX, 330, "ALGORYTM", f, akc + (int(240 * a),), CIEMNY + (int(255 * a),))
    for j, (cx, kol, n) in enumerate(((CX - 200, (110, 170, 240), 2), (CX + 200, (240, 140, 190), 5))):
        pj = wej(t, 0.2 + j * 0.3, 0.4)
        czlowiek(d, cx, 560, 70, kol, pj)
        for i in range(n):
            d.ellipse([cx - 50, 780 - i * 22, cx + 50, 810 - i * 22], fill=ZOLTY + (int(255 * pj),), outline=(150, 120, 20, int(255 * pj)), width=3)
    p2 = wej(t, 0.9, 0.5)
    strzalka(d, (CX, 400), (CX - 160, 470), ZIELONY, a, grub=8, postep=p2)
    if t > 1.3:
        pigulka(d, CX, 940, "TAŃSZE WYŚWIETLENIE WYGRYWA", f_anton(46), (60, 62, 72, 240), BIEL + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_dziewiatka": scena_pytanie_dziewiatka, "okazja": scena_okazja,
    "pytanie_format": scena_pytanie_format, "sledzony": scena_sledzony, "trzy_paski": scena_trzy_paski,
    "pytanie_algorytm": scena_pytanie_algorytm, "najtansze": scena_najtansze,
})


# ---------------------------------------------------------------- f1: czestotliwosc reklamy (21.11)

def _karta_reklamy(d, x0, y0, x1, a, akc):
    d.rounded_rectangle([x0, y0, x1, y0 + 200], radius=18, fill=(52, 52, 62, int(255 * a)))
    d.rounded_rectangle([x0 + 20, y0 + 20, x0 + 180, y0 + 180], radius=12, fill=akc + (int(255 * a),))
    d.rounded_rectangle([x0 + 210, y0 + 50, x1 - 40, y0 + 74], radius=8, fill=(170, 172, 182, int(255 * a)))
    d.rounded_rectangle([x0 + 210, y0 + 100, x1 - 140, y0 + 120], radius=8, fill=(120, 122, 134, int(255 * a)))


def scena_pytanie_czestotliwosc(im, t, dl, p, kt):
    """Ta sama reklama wraca w feedzie - licznik wyswietlen rosnie od startu."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, x1 = X0 + 40, X1 - 40
    for i in range(3):
        _karta_reklamy(d, x0, dol + 60 + i * 230, x1, 1.0 if i != 1 else 0.6, akc)
    n = 1 + int(min(t, dl) * 2.2)
    pigulka(d, x1 - 70, dol + 50, f"x{n}", f_anton(56), CZERW + (255,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_unika(im, t, dl, p, kt):
    """Po kilku razach czlowiek odwraca wzrok od reklamy."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _karta_reklamy(d, X0 + 40, 330, X1 - 40, a, akc)
    czlowiek(d, CX, 760, 100, BIEL, a)
    t1 = kt["czas_slowa"]("unikać") - kt["od"] - 0.15
    otw = 1 - wej(t, t1, 0.4)
    ik_oko(d, CX, 620, 50, akc, a, otwarcie=max(0.05, otw))
    if t > t1:
        strzalka(d, (CX + 120, 760), (CX + 300, 760), CZERW, 1.0, grub=9)
        pigulka(d, CX, 1000, "ZACZYNA UNIKAĆ", f_anton(52), CZERW + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_jeden_na(im, t, dl, p, kt):
    """N ludzikow, jeden robi sie czerwony na slowie - '1 na 4'."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    fb = dopasuj(d, tl, X1 - X0, 56, 36, f_anton)
    d.text((CX - szer(d, tl, fb) / 2, 320), tl, font=fb, fill=BIEL + (int(255 * a),))
    t0 = kt["czas_slowa"](p["start"]) - kt["od"] - 0.15
    q = wej(t, t0, 0.4)
    n = p.get("n", 4)
    for j in range(n):
        kol = CZERW if (j == n - 1 and q > 0) else (170, 172, 182)
        czlowiek(d, CX - (n - 1) * 110 + j * 220, 520, 80, kol, a)
    if q > 0:
        f = f_anton(int(200 * (0.9 + 0.1 * pop(t, t0, 0.4))))
        tx = p["liczba"]
        d.text((CX - szer(d, tx, f) / 2, 660), tx, font=f, fill=CZERW + (255,))
        fs = f_inter(38)
        for j, ln in enumerate(p.get("podpis", [])):
            d.text((CX - szer(d, ln, fs) / 2, 930 + j * 56), ln, font=fs, fill=BIEL + (int(255 * q),))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- f2: czas odpowiedzi na leada

def _zegar(d, cx, cy, r, t, a, kol=BIEL, spd=2.0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=kol + (int(255 * a),), width=8)
    for ang, dlg, gr in ((t * spd, 0.75, 8), (t * spd / 12, 0.5, 10)):
        d.line([cx, cy, cx + r * dlg * math.sin(ang), cy - r * dlg * math.cos(ang)], fill=kol + (int(255 * a),), width=gr)


def scena_pytanie_leady(im, t, dl, p, kt):
    """Skrzynka leadow z formularza, przy kazdym zegar - nikt nie oddzwania."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, x1 = X0 + 40, X1 - 40
    for i in range(3):
        y = dol + 70 + i * 170
        d.rounded_rectangle([x0, y, x1, y + 140], radius=16, fill=(52, 52, 62, 255))
        d.ellipse([x0 + 20, y + 30, x0 + 100, y + 110], fill=(120, 122, 134, 255))
        d.rounded_rectangle([x0 + 130, y + 40, x1 - 200, y + 62], radius=8, fill=(170, 172, 182, 255))
        d.rounded_rectangle([x0 + 130, y + 84, x1 - 280, y + 100], radius=8, fill=(120, 122, 134, 255))
        _zegar(d, x1 - 80, y + 70, 42, t + i, 1.0, kol=CZERW)
    pigulka(d, CX, dol + 600, "NIKT NIE ODDZWONIŁ", f_anton(46), CZERW + (int(255 * wej(t, 0.5, 0.4)),), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_czas_odp(im, t, dl, p, kt):
    """Zegar biegnie, lead blednie - liczy sie czas odpowiedzi."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _zegar(d, CX - 200, 560, 130, t * 3, a, kol=akc, spd=3.0)
    zan = max(0.2, 1 - t / max(dl, 0.1))
    czlowiek(d, CX + 200, 560, 90, BIEL, a * zan)
    t1 = kt["czas_slowa"]("czas") - kt["od"] - 0.15
    if t > t1:
        pigulka(d, CX, 860, "LICZY SIĘ CZAS ODPOWIEDZI", f_anton(48), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- f3: reklama online, zakup w sklepie

def _sklep(d, cx, cy, s, a):
    d.rectangle([cx - 110 * s, cy - 60 * s, cx + 110 * s, cy + 100 * s], fill=(90, 92, 104, int(255 * a)))
    for i in range(5):
        k = (CZERW if i % 2 == 0 else BIEL) + (int(255 * a),)
        d.rectangle([cx - 120 * s + i * 48 * s, cy - 100 * s, cx - 120 * s + (i + 1) * 48 * s, cy - 60 * s], fill=k)
    d.rectangle([cx - 30 * s, cy + 10 * s, cx + 30 * s, cy + 100 * s], fill=(30, 30, 36, int(255 * a)))


def scena_pytanie_offline(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 330
    # telefon z reklama
    d.rounded_rectangle([CX - 330, cy - 170, CX - 130, cy + 170], radius=26, fill=(30, 30, 36, 255), outline=(120, 122, 134, 255), width=5)
    d.rounded_rectangle([CX - 305, cy - 120, CX - 155, cy + 20], radius=12, fill=akc + (255,))
    strzalka(d, (CX - 100, cy), (CX + 80, cy), akc, 1.0, grub=9, postep=wej(t, 0.3, 0.6))
    _sklep(d, CX + 230, cy + 10, 1.0, 1.0)
    im.alpha_composite(nak)


def scena_do_sklepu(im, t, dl, p, kt):
    """Czlowiek widzi reklame w telefonie i idzie do sklepu."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _sklep(d, CX + 250, 600, 1.1, a)
    t1 = kt["czas_slowa"]("potem") - kt["od"] - 0.15
    q = wej(t, t1, 1.4)
    x = CX - 300 + 430 * q
    czlowiek(d, x, 600, 80, BIEL, a)
    d.rounded_rectangle([x - 110, 520, x - 60, 600], radius=8, fill=akc + (int(255 * a * (1 - q)),))
    if q > 0.6:
        pigulka(d, CX, 900, "KUPUJE W SKLEPIE", f_anton(50), ZIELONY + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_czestotliwosc": scena_pytanie_czestotliwosc, "unika": scena_unika, "jeden_na": scena_jeden_na,
    "pytanie_leady": scena_pytanie_leady, "czas_odp": scena_czas_odp,
    "pytanie_offline": scena_pytanie_offline, "do_sklepu": scena_do_sklepu,
})


# ---------------------------------------------------------------- g1: maly test reklamy (22.11)

def _szum(d, x0, x1, y, amp, t, a, kol, seed=3, efekt=0.0):
    import random as _r
    rr = _r.Random(seed)
    pts = []
    n = 26
    for i in range(n):
        v = rr.uniform(-1, 1) * amp + math.sin(i * 0.9 + t * 2) * amp * 0.25
        if i > n * 0.6:
            v -= efekt
        pts.append((x0 + (x1 - x0) * i / (n - 1), y + v))
    d.line(pts, fill=kol + (int(255 * a),), width=7, joint="curve")


def scena_pytanie_test(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, x1, y = X0 + 40, X1 - 40, dol + 330
    d.rounded_rectangle([x0 - 20, y - 220, x1 + 20, y + 220], radius=20, fill=(40, 40, 48, 230))
    _szum(d, x0, x1, y, 140, t, 1.0, BIEL)
    pigulka(d, x1 - 150, y - 180, "KRÓTKI TEST", f_anton(44), akc + (255,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_szum(im, t, dl, p, kt):
    """Sprzedaz skacze mocniej niz maly efekt reklamy - efekt ginie w szumie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    x0, x1 = X0 + 40, X1 - 40
    _szum(d, x0, x1, 560, 170, t, a, (170, 172, 182), efekt=25)
    q = wej(t, 0.6, 0.5)
    xe = x0 + (x1 - x0) * 0.62
    d.line([xe, 330, xe, 800], fill=akc + (int(255 * q),), width=4)
    f = f_inter(30)
    d.text((xe + 14, 330), "start reklamy", font=f, fill=akc + (int(255 * q),))
    t1 = kt["czas_slowa"]("mocniej") - kt["od"] - 0.15
    if t > t1:
        pigulka(d, CX, 900, "SPRZEDAŻ SKACZE SAMA Z SIEBIE", f_anton(44), (60, 62, 72, 240), BIEL + (255,))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- g2: lepsza oferta budzi klienta

def scena_pytanie_oferta(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 340
    d.rounded_rectangle([CX - 170, cy - 260, CX + 170, cy + 260], radius=36, fill=(30, 30, 36, 255), outline=(120, 122, 134, 255), width=6)
    q = wej(t, 0.2, 0.4)
    yb = cy - 180 + 40 * (1 - q)
    d.rounded_rectangle([CX - 140, yb, CX + 140, yb + 150], radius=22, fill=akc + (255,))
    f = f_anton(40)
    for j, ln in enumerate(("MAMY DLA CIEBIE", "LEPSZY PLAN!")):
        d.text((CX - szer(d, ln, f) / 2, yb + 22 + j * 52), ln, font=f, fill=CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_budzi(im, t, dl, p, kt):
    """Spokojny klient dostaje wiadomosc i zaczyna liczyc, ile placi."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, CX - 120, 600, 100, BIEL, a)
    t1 = kt["czas_slowa"]("płacą") - kt["od"] - 0.15
    q = wej(t, t1, 0.4)
    if q < 1:
        f = f_anton(60)
        for j in range(3):
            d.text((CX - 20 + j * 50, 430 - j * 50), "z", font=f, fill=(170, 172, 182, int(255 * a * (1 - q))))
    if q > 0:
        d.ellipse([CX + 20, 300, CX + 380, 520], fill=BIEL + (int(240 * q),))
        f2 = f_anton(54)
        d.text((CX + 200 - szer(d, "ILE PŁACĘ?", f2) / 2, 378), "ILE PŁACĘ?", font=f2, fill=CIEMNY + (int(255 * q),))
    t2 = kt["czas_slowa"]("zastanowić") - kt["od"] - 0.15
    if t > t2:
        pigulka(d, CX, 880, "ZACZYNA SIĘ ZASTANAWIAĆ", f_anton(48), CZERW + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- g3: male reklamy na telefonie

def scena_pytanie_baner(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 340
    d.rounded_rectangle([CX - 170, cy - 260, CX + 170, cy + 260], radius=36, fill=(30, 30, 36, 255), outline=(120, 122, 134, 255), width=6)
    for i in range(5):
        d.rounded_rectangle([CX - 130, cy - 210 + i * 60, CX + 130 - (i % 2) * 60, cy - 186 + i * 60], radius=8, fill=(120, 122, 134, 255))
    pq = 0.75 + 0.25 * math.sin(t * 5)
    d.rounded_rectangle([CX - 140, cy + 150, CX + 140, cy + 220], radius=10, fill=akc + (int(255 * pq),))
    im.alpha_composite(nak)


def scena_przypomnienie(im, t, dl, p, kt):
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    d.rounded_rectangle([CX - 300, 400, CX - 60, 470], radius=10, fill=akc + (int(255 * a),))
    strzalka(d, (CX - 40, 435), (CX + 80, 435), akc, a, grub=8, postep=wej(t, 0.3, 0.5))
    czlowiek(d, CX + 200, 470, 90, BIEL, a)
    t1 = kt["czas_slowa"]("przypomnienie") - kt["od"] - 0.15
    if t > t1:
        pigulka(d, CX + 200, 250, "AHA, NO TAK", f_anton(44), BIEL + (240,), CIEMNY + (255,))
        pigulka(d, CX, 760, "PRZYPOMINA, NIE UCZY", f_anton(50), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_pasuje(im, t, dl, p, kt):
    """Dwie kolumny: praktyczne (ptaszek) vs drobiazgi (krzyzyk), kazda na swoim slowie."""
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    fb = dopasuj(d, tl, X1 - X0, 56, 36, f_anton)
    d.text((CX - szer(d, tl, fb) / 2, 320), tl, font=fb, fill=BIEL + (int(255 * a),))
    for j, (cx, et, sl, ok) in enumerate(((CX - 210, p["lewa"], p["od_lewa"], True), (CX + 210, p["prawa"], p["od_prawa"], False))):
        t0 = kt["czas_slowa"](sl) - kt["od"] - 0.15
        q = wej(t, t0, 0.4)
        d.rounded_rectangle([cx - 190, 440, cx + 190, 900], radius=24, fill=(52, 52, 62, int(255 * a)))
        fs = f_inter(34)
        for i, ln in enumerate(et):
            d.text((cx - szer(d, ln, fs) / 2, 480 + i * 50), ln, font=fs, fill=BIEL + (int(255 * a),))
        if q > 0:
            if ok:
                ptaszek(d, cx, 740, 90 * q, 1.0)
            else:
                krzyzyk(d, cx, 740, 80, 1.0, q)
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_test": scena_pytanie_test, "szum": scena_szum,
    "pytanie_oferta": scena_pytanie_oferta, "budzi": scena_budzi,
    "pytanie_baner": scena_pytanie_baner, "przypomnienie": scena_przypomnienie, "pasuje": scena_pasuje,
})


# ---------------------------------------------------------------- h1: logo w reklamie wideo (23.11)

def _odtwarzacz(d, x0, y0, x1, y1, a):
    d.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=(30, 30, 36, int(255 * a)), outline=(90, 92, 104, int(255 * a)), width=4)
    d.rounded_rectangle([x0 + 20, y1 - 40, x1 - 20, y1 - 28], radius=6, fill=(90, 92, 104, int(255 * a)))


def scena_pytanie_logo(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, y0, x1, y1 = X0 + 40, dol + 80, X1 - 40, dol + 620
    _odtwarzacz(d, x0, y0, x1, y1, 1.0)
    d.rounded_rectangle([CX - 160, (y0 + y1) / 2 - 110, CX + 160, (y0 + y1) / 2 + 90], radius=30, fill=akc + (255,))
    f = f_anton(90)
    d.text((CX - szer(d, "LOGO", f) / 2, (y0 + y1) / 2 - 80), "LOGO", font=f, fill=CIEMNY + (255,))
    q = 0.55 + 0.45 * math.sin(t * 6)
    pigulka(d, x1 - 120, y1 - 100, "POMIŃ", f_anton(44), BIEL + (int(255 * q),), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_przewija(im, t, dl, p, kt):
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _odtwarzacz(d, X0 + 80, 330, X1 - 80, 700, a)
    d.rounded_rectangle([CX - 110, 440, CX + 110, 560], radius=20, fill=akc + (int(255 * a),))
    t1 = kt["czas_slowa"]("przewija") - kt["od"] - 0.2
    q = wej(t, t1, 0.5)
    if q > 0:
        y = 780 - 260 * q
        d.ellipse([CX + 160, y - 40, CX + 240, y + 40], fill=BIEL + (int(255 * (1 - q * 0.5)),))
        strzalka(d, (CX + 200, 820), (CX + 200, 620), BIEL, 1.0, grub=8)
        pigulka(d, CX, 900, "WIDZI LOGO = PRZEWIJA", f_anton(50), CZERW + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_os_czasu(im, t, dl, p, kt):
    """Dwie osie czasu reklamy: logo dlugo na poczatku (krzyzyk) vs krotko kilka razy (ptaszek)."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    fb = dopasuj(d, tl, X1 - X0, 56, 36, f_anton)
    d.text((CX - szer(d, tl, fb) / 2, 320), tl, font=fb, fill=BIEL + (int(255 * a),))
    x0, x1 = X0 + 40, X1 - 40
    fs = f_inter(32)
    for j, (et, bloki, ok) in enumerate((("długo na początku", [(0.0, 0.35)], False),
                                          ("krótko, kilka razy", [(0.0, 0.08), (0.33, 0.41), (0.66, 0.74), (0.92, 1.0)], True))):
        y = 450 + j * 190
        pj = wej(t, 0.2 + j * 0.5, 0.4)
        d.text((x0, y), et, font=fs, fill=BIEL + (int(255 * pj),))
        d.rounded_rectangle([x0, y + 50, x1 - 110, y + 100], radius=14, fill=(60, 62, 72, int(255 * pj)))
        for b0, b1 in bloki:
            d.rounded_rectangle([x0 + (x1 - 110 - x0) * b0, y + 50, x0 + (x1 - 110 - x0) * b1, y + 100], radius=14, fill=akc + (int(255 * pj),))
        if pj > 0.5:
            if ok:
                ptaszek(d, x1 - 45, y + 75, 40, 1.0)
            else:
                krzyzyk(d, x1 - 45, y + 75, 36, 1.0, 1.0)
    t0 = kt["czas_slowa"](p["start"]) - kt["od"] - 0.15
    q = pop(t, t0, 0.45)
    if q > 0:
        f = f_anton(max(1, int(120 * q)))
        d.text((CX - szer(d, p["liczba"], f) / 2, 850), p["liczba"], font=f, fill=ZIELONY + (255,))
        fs2 = f_inter(38)
        d.text((CX - szer(d, p["podpis"], fs2) / 2, 1000), p["podpis"], font=fs2, fill=BIEL + (int(255 * min(1, q)),))
    im.alpha_composite(nak)


# ---------------------------------------------------------------- h2/h3: Black Friday

def _metka_bf(d, cx, cy, a, akc, s=1.0):
    w, h = 300 * s, 150 * s
    d.polygon([(cx - w / 2, cy - h / 2), (cx + w / 2 - 50 * s, cy - h / 2), (cx + w / 2, cy), (cx + w / 2 - 50 * s, cy + h / 2),
               (cx - w / 2, cy + h / 2)], fill=(20, 20, 24, int(255 * a)), outline=akc + (int(255 * a),))
    f = f_anton(int(46 * s))
    for j, ln in enumerate(("BLACK", "FRIDAY")):
        d.text((cx - 25 * s - szer(d, ln, f) / 2, cy - 56 * s + j * 52 * s), ln, font=f, fill=BIEL + (int(255 * a),))


def scena_pytanie_bf(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 300
    _metka_bf(d, CX - 120, cy, 1.0, akc, s=1.3)
    q = wej(t, 0.3, 0.8)
    for i in range(int(1 + 4 * q)):
        d.ellipse([CX + 180, cy + 120 - i * 34, CX + 300, cy + 160 - i * 34], fill=ZOLTY + (255,), outline=(150, 120, 20, 255), width=3)
    strzalka(d, (CX + 350, cy + 140), (CX + 350, cy - 60), CZERW, 1.0, grub=10, postep=q)
    im.alpha_composite(nak)


def scena_drozeje(im, t, dl, p, kt):
    """Wyswietlenie drozeje, ale ludzie chetniej kupuja - dwie strzalki w gore na slowach."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    f = f_anton(52)
    for j, (et, sl, kol) in enumerate((("WYŚWIETLENIE DROŻEJE", "drożeje", CZERW), ("LUDZIE CHĘTNIEJ KUPUJĄ", "chętniej", ZIELONY))):
        t0 = kt["czas_slowa"](sl) - kt["od"] - 0.15
        q = wej(t, t0, 0.4)
        y = 420 + j * 260
        d.text((X0 + 40, y), et, font=f, fill=BIEL + (int(255 * max(0.25 * a, q)),))
        if q > 0:
            strzalka(d, (X1 - 80, y + 150), (X1 - 80, y - 10), kol, 1.0, grub=12, postep=q)
            czlowiek(d, X0 + 90, y + 140, 40, kol, q) if j == 1 else None
    im.alpha_composite(nak)


def scena_pytanie_bf2(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    x0, x1, yb = X0 + 60, X1 - 60, dol + 560
    vals = [0.35, 0.32, 0.3, 0.28, 1.0, 0.3, 0.27, 0.32]
    w = (x1 - x0) / len(vals)
    q = wej(t, 0.2, 0.8)
    for i, v in enumerate(vals):
        h = 420 * v * (q if i == 4 else 1)
        kol = akc if i == 4 else (120, 122, 134)
        d.rounded_rectangle([x0 + i * w + 8, yb - h, x0 + (i + 1) * w - 8, yb], radius=10, fill=kol + (255,))
    im.alpha_composite(nak)


def scena_przed_po(im, t, dl, p, kt):
    """Przed szczytem klienci czekaja, po szczycie odpoczywaja - slupki z podpisami na slowach."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    x0, x1, yb = X0 + 40, X1 - 40, 800
    vals = [0.5, 0.25, 0.22, 1.0, 0.2, 0.24, 0.5]
    w = (x1 - x0) / len(vals)
    for i, v in enumerate(vals):
        kol = akc if i == 3 else (120, 122, 134)
        d.rounded_rectangle([x0 + i * w + 8, yb - 420 * v, x0 + (i + 1) * w - 8, yb], radius=10, fill=kol + (int(255 * a),))
    f = f_anton(40)
    for sl, x, et in (("czekają", x0 + w * 1.5, "CZEKAJĄ"), ("odpoczywają", x0 + w * 5.5, "ODPOCZYWAJĄ")):
        t0 = kt["czas_slowa"](sl) - kt["od"] - 0.15
        if t > t0:
            pigulka(d, x, yb + 70, et, f, CZERW + (240,), CIEMNY + (255,))
            d.rounded_rectangle([x - w, yb - 240, x + w, yb], radius=12, outline=CZERW + (255,), width=5)
    pigulka(d, x0 + w * 3.5, yb - 470, "SZCZYT", f, akc + (int(240 * a),), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_logo": scena_pytanie_logo, "przewija": scena_przewija, "os_czasu": scena_os_czasu,
    "pytanie_bf": scena_pytanie_bf, "drozeje": scena_drozeje,
    "pytanie_bf2": scena_pytanie_bf2, "przed_po": scena_przed_po,
})


# ---------------------------------------------------------------- i1/i3: prawdziwa obnizka, porzucony koszyk

def _wykres_ceny(d, x0, y0, x1, y1, a, akc, q=1.0):
    """Historia ceny z roku: plaska linia, w listopadzie ten sam poziom."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(40, 42, 50, int(235 * a)))
    pts = [0.55, 0.5, 0.56, 0.52, 0.5, 0.54, 0.51, 0.55, 0.52, 0.5, 0.53, 0.52]
    n = max(2, int(len(pts) * q))
    w = (x1 - x0 - 60) / (len(pts) - 1)
    xy = [(x0 + 30 + i * w, y0 + 30 + (y1 - y0 - 60) * pts[i]) for i in range(n)]
    d.line(xy, fill=akc + (int(255 * a),), width=7)


def scena_pytanie_promo(im, t, dl, p, kt):
    """Metka Black Friday i przekreslona stara cena ze znakiem zapytania - od pierwszej klatki."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 300
    _metka_bf(d, CX - 190, cy, 1.0, akc, s=1.2)
    _metka_ceny(d, CX + 210, cy - 70, "-50%", ZOLTY, 1.0, s=1.0)
    f = f_anton(int(150 * (0.9 + 0.1 * pop(t, 0.3, 0.5))))
    d.text((CX + 190 - szer(d, "?", f) / 2, cy - 10), "?", font=f, fill=BIEL + (255,))
    im.alpha_composite(nak)


def scena_sprawdza(im, t, dl, p, kt):
    """Klient z telefonem sprawdza historie ceny - linia plaska, obnizka nie jest prawdziwa."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, X0 + 150, 560, 90, BIEL, a)
    tx0, ty0, tx1, ty1 = CX - 60, 360, X1 - 30, 780
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=34, fill=(28, 28, 34, int(255 * a)), outline=(150, 152, 162, int(255 * a)), width=5)
    t1 = kt["czas_slowa"](p.get("slowo", "sprawdzić")) - kt["od"] - 0.15
    _wykres_ceny(d, tx0 + 24, ty0 + 60, tx1 - 24, ty1 - 60, a, akc, q=0.3 + 0.7 * wej(t, t1, 0.8))
    if t > t1 + 0.4:
        pigulka(d, CX, 900, "KLIENT SPRAWDZA HISTORIĘ CENY", f_anton(44), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def _koszyk(d, cx, cy, s, a, kol=BIEL, pelny=True, akc=ZOLTY):
    w, h = 200 * s, 130 * s
    d.line([(cx - w / 2 - 50 * s, cy - h / 2 - 30 * s), (cx - w / 2, cy - h / 2)], fill=kol + (int(255 * a),), width=int(9 * s))
    d.polygon([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2 - 25 * s, cy + h / 2), (cx - w / 2 + 25 * s, cy + h / 2)],
              outline=kol + (int(255 * a),), width=int(8 * s))
    for k in (-1, 1):
        x = cx + k * w * 0.3
        d.ellipse([x - 16 * s, cy + h / 2 + 12 * s, x + 16 * s, cy + h / 2 + 44 * s], fill=kol + (int(255 * a),))
    if pelny:
        for j, kk in enumerate((akc, (110, 170, 240), (240, 140, 190))):
            x = cx - w * 0.3 + j * w * 0.3
            d.rounded_rectangle([x - 26 * s, cy - h / 2 - 50 * s, x + 26 * s, cy - h / 2 + 6 * s], radius=int(8 * s), fill=kk + (int(255 * a),))


def scena_pytanie_koszyk(im, t, dl, p, kt):
    """Porzucony koszyk z rzeczami i telefon z przychodzaca wiadomoscia - od pierwszej klatki."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 320
    _koszyk(d, CX - 170, cy + 30, 1.3, 1.0, akc=akc)
    tx0, ty0 = CX + 140, cy - 170
    d.rounded_rectangle([tx0, ty0, tx0 + 190, ty0 + 340], radius=28, fill=(28, 28, 34, 255), outline=(150, 152, 162, 255), width=5)
    q = pop(t, 0.3, 0.5)
    if q > 0:
        d.rounded_rectangle([tx0 + 20, ty0 + 70, tx0 + 20 + 150 * q, ty0 + 70 + 90 * q], radius=16, fill=akc + (255,))
        for j in range(2):
            d.rounded_rectangle([tx0 + 36, ty0 + 92 + j * 30, tx0 + 36 + 100 * q, ty0 + 104 + j * 30], radius=6, fill=CIEMNY + (int(255 * q),))
    im.alpha_composite(nak)


def scena_wie_co(im, t, dl, p, kt):
    """Klient z dymkiem, w ktorym jest jego koszyk - wie, co zostawil, przypomnienie nic nie wnosi."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, CX - 200, 620, 100, BIEL, a)
    for j, r in enumerate((14, 22)):
        d.ellipse([CX - 110 + j * 50 - r, 470 - j * 40 - r, CX - 110 + j * 50 + r, 470 - j * 40 + r], fill=(70, 72, 84, int(255 * a)))
    d.ellipse([CX - 30, 230, CX + 360, 470], fill=(70, 72, 84, int(255 * a)))
    _koszyk(d, CX + 165, 360, 0.8, a, akc=akc)
    t1 = kt["czas_slowa"](p.get("slowo", "wie")) - kt["od"] - 0.15
    if t > t1:
        pigulka(d, CX, 900, "DOBRZE WIE, CO ZOSTAWIŁ", f_anton(48), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_promo": scena_pytanie_promo, "sprawdza": scena_sprawdza,
    "pytanie_koszyk": scena_pytanie_koszyk, "wie_co": scena_wie_co,
})


# ---------------------------------------------------------------- i2: twarz w reklamie

def _zdjecie(d, x, y, w, a, twarz, akc):
    """Kwadratowe zdjecie: z twarza (glowa + ramiona) albo z samym pudelkiem produktu."""
    A = int(255 * a)
    d.rounded_rectangle([x, y, x + w, y + w], radius=18, fill=(58, 60, 70, A))
    cx = x + w / 2
    if twarz:
        r = w * 0.2
        d.ellipse([cx - r, y + w * 0.2, cx + r, y + w * 0.2 + 2 * r], fill=(232, 190, 160, A))
        d.ellipse([cx - r * 0.45, y + w * 0.36, cx - r * 0.25, y + w * 0.42], fill=CIEMNY + (A,))
        d.ellipse([cx + r * 0.25, y + w * 0.36, cx + r * 0.45, y + w * 0.42], fill=CIEMNY + (A,))
        d.arc([cx - r * 0.45, y + w * 0.38, cx + r * 0.45, y + w * 0.55], 20, 160, fill=CIEMNY + (A,), width=4)
        d.pieslice([cx - w * 0.36, y + w * 0.66, cx + w * 0.36, y + w * 1.2], 180, 360, fill=akc + (A,))
    else:
        d.rectangle([cx - w * 0.22, y + w * 0.3, cx + w * 0.22, y + w * 0.78], fill=(150, 152, 162, A))
        d.polygon([(cx - w * 0.22, y + w * 0.3), (cx - w * 0.1, y + w * 0.2), (cx + w * 0.32, y + w * 0.2), (cx + w * 0.22, y + w * 0.3)],
                  fill=(185, 187, 197, A))


def scena_pytanie_twarz(im, t, dl, p, kt):
    """Dwie reklamy obok siebie: sam produkt i czlowiek - od pierwszej klatki."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    y = dol + 140
    _zdjecie(d, CX - 340, y, 300, 1.0, False, akc)
    _zdjecie(d, CX + 40, y, 300, 1.0, True, akc)
    f = f_anton(int(120 * (0.9 + 0.1 * pop(t, 0.3, 0.5))))
    d.text((CX - szer(d, "?", f) / 2, y + 80), "?", font=f, fill=BIEL + (255,))
    im.alpha_composite(nak)


def scena_wzrok(im, t, dl, p, kt):
    """Oko skanuje kadr i laduje na twarzy, zanim zauwazy produkt."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _zdjecie(d, X0 + 60, 520, 300, a, False, akc)
    _zdjecie(d, X1 - 360, 520, 300, a, True, akc)
    ox, oy = CX, 360
    d.ellipse([ox - 90, oy - 45, ox + 90, oy + 45], outline=BIEL + (int(255 * a),), width=6)
    q = wej(t, 0.2, 1.0)
    tx, ty = X1 - 210, 640
    px, py = ox + 40 * q, oy + 12 * q          # zrenica zostaje w oku i patrzy w strone twarzy
    d.ellipse([px - 30, py - 30, px + 30, py + 30], fill=akc + (int(255 * a),))
    d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=CIEMNY + (int(255 * a),))
    if q > 0:
        strzalka(d, (ox + 40, oy + 50), (tx - 20, ty - 70), akc, a, grub=8, postep=q)
    t1 = kt["czas_slowa"](p.get("slowo", "twarzy")) - kt["od"] - 0.15
    if t > t1:
        d.rounded_rectangle([X1 - 372, 508, X1 - 48, 832], radius=22, outline=akc + (255,), width=8)
        pigulka(d, CX, 960, "WZROK SAM SZUKA TWARZY", f_anton(48), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({"pytanie_twarz": scena_pytanie_twarz, "wzrok": scena_wzrok})


# ---------------------------------------------------------------- j1-j3: okres probny, klient ze znizki, najczesciej wybierane

def _bilet(d, cx, cy, tekst, kol, a, s=1.0):
    w, h = 380 * s, 170 * s
    A = int(255 * a)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(20 * s), fill=kol + (A,))
    for k in (-1, 1):
        d.ellipse([cx + k * w / 2 - 22 * s, cy - 22 * s, cx + k * w / 2 + 22 * s, cy + 22 * s], fill=(28, 28, 34, A))
    f = f_anton(int(70 * s))
    d.text((cx - szer(d, tekst, f) / 2, cy - f.size * 0.62), tekst, font=f, fill=CIEMNY + (A,))


def scena_pytanie_proba(im, t, dl, p, kt):
    """Bilet ZA DARMO i ludzie, ktorzy po niego ida - od pierwszej klatki."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 260
    _bilet(d, CX, cy, "ZA DARMO", akc, 1.0, s=1.2)
    for j in range(4):
        x = CX - 330 + j * 220 - 30 * wej(t, 0.2, 1.2)
        czlowiek(d, x, cy + 290, 55, ((110, 170, 240), (240, 140, 190))[j % 2], 1.0)
    im.alpha_composite(nak)


def scena_po_darmowe(im, t, dl, p, kt):
    """Ludzie przychodza po darmowe, a gdy trzeba placic - odchodza."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _bilet(d, CX + 150, 430, "ZA DARMO", akc, a, s=0.9)
    _bilet(d, CX + 150, 720, "PŁATNE", (150, 152, 162), a, s=0.9)
    t1 = kt["czas_slowa"](p.get("slowo", "darmo")) - kt["od"] - 0.15
    q = wej(t, max(0.2, t1 - 0.8), 1.0)
    for j in range(3):
        czlowiek(d, X0 + 60 + j * 90, 430, 40, BIEL, a)
    strzalka(d, (X0 + 270, 430), (CX - 40, 430), akc, a, grub=8, postep=wej(t, 0.2, 0.6))
    if q > 0:
        strzalka(d, (CX - 40, 740), (X0 + 120, 740), CZERW, 1.0, grub=10, postep=q)
        f = f_inter(32)
        d.text((X0 + 120, 790), "odchodzą", font=f, fill=CZERW + (int(255 * q),))
    if t > t1:
        pigulka(d, CX, 960, "PRZYSZLI PO DARMOWE", f_anton(48), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_pytanie_znizka(im, t, dl, p, kt):
    """Duza metka -35% i klient przed nia - od pierwszej klatki."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 300
    _metka_ceny(d, CX + 110, cy, "-35%", ZOLTY, 1.0, s=1.5 * (0.95 + 0.05 * pop(t, 0.2, 0.5)))
    czlowiek(d, CX - 260, cy + 40, 85, BIEL, 1.0)
    im.alpha_composite(nak)


def scena_po_cene(im, t, dl, p, kt):
    """Klient idzie za metka, nie za firma: metka znika, klient odchodzi."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _sklep(d, X0 + 170, 560, 1.0, a)
    t1 = kt["czas_slowa"](p.get("slowo", "cenę")) - kt["od"] - 0.15
    q = wej(t, t1, 0.8)
    _metka_ceny(d, CX + 160 + 120 * q, 440, "-35%", ZOLTY, a * (1 - 0.6 * q), s=1.0)
    czlowiek(d, CX + 40 + 220 * q, 640, 70, BIEL, a)
    if q > 0:
        strzalka(d, (CX - 40, 760), (CX + 300, 760), akc, 1.0, grub=8, postep=q)
        pigulka(d, CX, 960, "PRZYSZEDŁ PO CENĘ", f_anton(48), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def _menu(d, x0, y0, x1, a, akc, wyroz=None, n=5):
    A = int(255 * a)
    d.rounded_rectangle([x0, y0, x1, y0 + 90 + n * 80], radius=22, fill=(240, 236, 226, A))
    for i in range(n):
        y = y0 + 50 + i * 80
        d.rounded_rectangle([x0 + 40, y, x0 + 40 + (x1 - x0) * (0.45 + 0.08 * (i % 3)), y + 22], radius=8, fill=(120, 116, 108, A))
        d.rounded_rectangle([x1 - 120, y, x1 - 40, y + 22], radius=8, fill=(160, 156, 148, A))
        if wyroz is not None and i in wyroz:
            d.rounded_rectangle([x0 + 14, y - 16, x1 - 14, y + 40], radius=12, outline=akc + (A,), width=6)


def scena_pytanie_bestseller(im, t, dl, p, kt):
    """Karta menu z jedna pozycja wyroznionej odznaka - od pierwszej klatki."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    y0 = dol + 90
    _menu(d, CX - 300, y0, CX + 300, 1.0, akc, wyroz=[1])
    q = pop(t, 0.3, 0.5)
    if q > 0:
        pigulka(d, CX + 220, y0 + 100, "NAJCZĘŚCIEJ WYBIERANE", f_anton(int(34 * max(q, 0.01))), akc + (255,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_patrzy_na_innych(im, t, dl, p, kt):
    """Niepewny klient (znak zapytania) patrzy na innych, ktorzy wybieraja to samo danie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    czlowiek(d, CX, 700, 90, BIEL, a)
    f = f_anton(110)
    d.text((CX - szer(d, "?", f) / 2, 470), "?", font=f, fill=BIEL + (int(255 * a),))
    t1 = kt["czas_slowa"](p.get("slowo", "inni")) - kt["od"] - 0.15
    for j, x in enumerate((X0 + 110, X0 + 260, X1 - 260, X1 - 110)):
        q = wej(t, max(0.3, t1 - 1.0) + j * 0.15, 0.4)
        czlowiek(d, x, 470, 50, ((110, 170, 240), (240, 140, 190))[j % 2], a)
        if q > 0:
            strzalka(d, (x, 540), (CX + (x - CX) * 0.35, 840), akc, q, grub=6, postep=q)
    d.rounded_rectangle([CX - 90, 840, CX + 90, 900], radius=16, fill=akc + (int(255 * a),))
    if t > t1:
        pigulka(d, CX, 1000, "PATRZY, CO WYBIERAJĄ INNI", f_anton(46), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_proba": scena_pytanie_proba, "po_darmowe": scena_po_darmowe,
    "pytanie_znizka": scena_pytanie_znizka, "po_cene": scena_po_cene,
    "pytanie_bestseller": scena_pytanie_bestseller, "patrzy_na_innych": scena_patrzy_na_innych,
})


# ---------------------------------------------------------------- k1-k3: piec gwiazdek, kupione dane, przeprosiny

def _ocena(d, x0, y0, x1, ocena, n, a, obrys=None):
    A = int(255 * a)
    d.rounded_rectangle([x0, y0, x1, y0 + 230], radius=22, fill=(52, 52, 62, A), outline=(obrys + (A,)) if obrys else None, width=6)
    f = f_anton(90)
    d.text(((x0 + x1) / 2 - szer(d, ocena, f) / 2, y0 + 20), ocena, font=f, fill=BIEL + (A,))
    r = (x1 - x0) / 13
    _gwiazdki(d, (x0 + x1) / 2 - r * 4.6, y0 + 180, n, r, a)


def scena_pytanie_gwiazdki(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    y = dol + 140
    _ocena(d, CX - 360, y, CX - 30, "5,0", 5, 1.0)
    _ocena(d, CX + 30, y, CX + 360, "4,5", 4, 1.0)
    f = f_anton(int(110 * (0.9 + 0.1 * pop(t, 0.3, 0.5))))
    d.text((CX - szer(d, "?", f) / 2, y + 300), "?", font=f, fill=BIEL + (255,))
    im.alpha_composite(nak)


def scena_podejrzane(im, t, dl, p, kt):
    """Ocena 5,0 pod lupa klienta - wyglada za idealnie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    _ocena(d, CX - 220, 420, CX + 220, "5,0", 5, a)
    czlowiek(d, X0 + 120, 760, 70, BIEL, a)
    q = wej(t, 0.3, 0.8)
    lx, ly = CX + 140 - 80 * q, 560
    d.ellipse([lx - 80, ly - 80, lx + 80, ly + 80], outline=akc + (int(255 * a),), width=10)
    d.line([lx + 56, ly + 56, lx + 130, ly + 130], fill=akc + (int(255 * a),), width=16)
    t1 = kt["czas_slowa"](p.get("slowo", "podejrzanie")) - kt["od"] - 0.15
    if t > t1:
        pigulka(d, CX, 960, "WYGLĄDA ZA IDEALNIE", f_anton(50), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_krzywa_ocen(im, t, dl, p, kt):
    """Krzywa checi zakupu od oceny: rosnie do 4-4,7, spada przy 5. Pasmo szczytu na slowie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    fb = dopasuj(d, tl, X1 - X0, 56, 36, f_anton)
    d.text((CX - szer(d, tl, fb) / 2, 320), tl, font=fb, fill=BIEL + (int(255 * a),))
    x0, x1, yb, yt = X0 + 60, X1 - 60, 900, 480
    d.line([x0, yb, x1, yb], fill=(150, 152, 162, int(255 * a)), width=4)
    fx = f_inter(34)
    def X(v):
        return x0 + (v - 3.0) / 2.0 * (x1 - x0)
    for v, et in ((3.0, "3"), (4.0, "4"), (4.7, "4,7"), (5.0, "5")):
        d.text((X(v) - szer(d, et, fx) / 2, yb + 14), et, font=fx, fill=BIEL + (int(255 * a),))
    t1 = kt["czas_slowa"](p.get("start", "zakupu")) - kt["od"] - 0.15
    q = wej(t, t1, 1.2)
    if t > t1 + 0.4:
        d.rectangle([X(4.0), yt - 20, X(4.7), yb], fill=akc[:3] + (60,))
    def krzywa(qq):
        out = []
        for i in range(int(60 * qq) + 1):
            v = 3.0 + 2.0 * i / 60
            h = 0.35 + 0.65 * (1 - ((v - 4.35) / 1.0) ** 2) if v <= 4.7 else 0.35 + 0.65 * (1 - (0.35) ** 2) - 0.9 * (v - 4.7)
            out.append((X(v), yb - (yb - yt) * max(0.05, h)))
        return out
    # szary zarys krzywej trzyma kadr, zanim padnie liczba
    d.line(krzywa(1.0), fill=(120, 122, 134, int(150 * a)), width=5)
    pts = []
    n = 60
    for i in range(int(n * q) + 1):
        v = 3.0 + 2.0 * i / n
        h = 0.35 + 0.65 * (1 - ((v - 4.35) / 1.0) ** 2) if v <= 4.7 else 0.35 + 0.65 * (1 - (0.35) ** 2) - 0.9 * (v - 4.7)
        pts.append((X(v), yb - (yb - yt) * max(0.05, h)))
    if len(pts) > 1:
        d.line(pts, fill=ZIELONY + (255,), width=9)
    t2 = kt["czas_slowa"](p.get("spadek", "spadała")) - kt["od"] - 0.15
    if t > t2:
        strzalka(d, (X(4.8), yt + 120), (X(4.97), yt + 300), CZERW, 1.0, grub=10, postep=wej(t, t2, 0.4))
        pigulka(d, CX, 1010, "SZCZYT: 4-4,7", f_anton(50), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def _moneta(d, cx, cy, r, a, kat=0.0):
    A = int(255 * a)
    sx = 0.3 + 0.7 * abs(math.cos(kat))
    d.ellipse([cx - r * sx, cy - r, cx + r * sx, cy + r], fill=ZOLTY + (A,), outline=(150, 120, 20, A), width=6)
    if sx > 0.4:
        f = f_anton(int(r * 0.9 * sx))
        tx = "?"
        d.text((cx - szer(d, tx, f) / 2, cy - f.size * 0.62), tx, font=f, fill=(150, 120, 20, A))


def scena_pytanie_celowanie(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 330
    for j, kol in enumerate(((110, 170, 240), (240, 140, 190), (110, 170, 240), (240, 140, 190), (110, 170, 240))):
        czlowiek(d, CX - 360 + j * 180, cy + 40, 50, kol, 1.0)
    cx = CX - 180 + 360 * (0.5 + 0.5 * math.sin(t * 1.4))
    for r in (150, 95):
        d.ellipse([cx - r, cy + 40 - r, cx + r, cy + 40 + r], outline=akc + (255,), width=7)
    d.line([cx - 180, cy + 40, cx + 180, cy + 40], fill=akc + (220,), width=4)
    d.line([cx, cy - 140, cx, cy + 220], fill=akc + (220,), width=4)
    im.alpha_composite(nak)


def scena_zgadywane(im, t, dl, p, kt):
    """Profil klienta z polami wypelnionymi znakami zapytania."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    A = int(255 * a)
    x0, y0, x1 = CX - 300, 380, CX + 300
    d.rounded_rectangle([x0, y0, x1, y0 + 470], radius=24, fill=(52, 52, 62, A))
    czlowiek(d, x0 + 110, y0 + 150, 60, BIEL, a)
    f = f_anton(46)
    for j, et in enumerate(("PŁEĆ", "WIEK", "ZAINTERESOWANIA")):
        y = y0 + 260 + j * 64
        d.text((x0 + 40, y), et, font=f_inter(34), fill=BIEL + (A,))
        q = pop(t, 0.3 + j * 0.25, 0.4)
        if q > 0:
            d.text((x1 - 80, y - 8), "?", font=f, fill=akc + (int(255 * min(1, q)),))
    t1 = kt["czas_slowa"](p.get("slowo", "zgadywane")) - kt["od"] - 0.15
    if t > t1:
        pigulka(d, CX, 960, "DANE CZĘSTO ZGADYWANE", f_anton(50), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


def scena_moneta_koszt(im, t, dl, p, kt):
    """Moneta (plec jak rzut moneta) od wejscia, potem +151% kosztu na slowie."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    tl = p.get("tytul", "")
    fb = dopasuj(d, tl, X1 - X0, 56, 36, f_anton)
    d.text((CX - szer(d, tl, fb) / 2, 320), tl, font=fb, fill=BIEL + (int(255 * a),))
    _moneta(d, CX, 560, 120, a, kat=t * 5.0)
    t1 = kt["czas_slowa"](p["slowo1"]) - kt["od"] - 0.15
    if t > t1:
        pigulka(d, CX, 730, p.get("et1", "PŁEĆ: JAK RZUT MONETĄ"), f_anton(48), akc + (240,), CIEMNY + (255,))
    t2 = kt["czas_slowa"](p["slowo2"]) - kt["od"] - 0.15
    q = wej(t, t2, 0.7)
    if q > 0:
        v = p["wartosc"] * q
        tx = f"+{int(round(v))}%"
        f = f_anton(int(170 * (0.9 + 0.1 * pop(t, t2, 0.4))))
        d.text((CX - szer(d, tx, f) / 2, 820), tx, font=f, fill=CZERW + (255,))
        fs = f_inter(40)
        d.text((CX - szer(d, p["podpis2"], fs) / 2, 1050), p["podpis2"], font=fs, fill=BIEL + (int(255 * q),))
    im.alpha_composite(nak)


def _paczka2(d, cx, cy, s, a, akc):
    A = int(255 * a)
    w, h = 260 * s, 200 * s
    d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=(196, 150, 96, A))
    d.rectangle([cx - 20 * s, cy - h / 2, cx + 20 * s, cy + h / 2], fill=(160, 120, 70, A))


def scena_pytanie_paczka(im, t, dl, p, kt):
    """Paczka i zegar ze wskazowka po terminie - od pierwszej klatki."""
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 300
    _paczka2(d, CX - 150, cy + 40, 1.2, 1.0, akc)
    r = 120
    zx = CX + 220
    d.ellipse([zx - r, cy - r, zx + r, cy + r], fill=(240, 240, 244, 255), outline=CZERW + (255,), width=10)
    ang = -math.pi / 2 + t * 2.2
    d.line([zx, cy, zx + r * 0.8 * math.cos(ang), cy + r * 0.8 * math.sin(ang)], fill=CIEMNY + (255,), width=8)
    d.line([zx, cy, zx, cy - r * 0.5], fill=CIEMNY + (255,), width=10)
    im.alpha_composite(nak)


def scena_tanie_slowa(im, t, dl, p, kt):
    """Dymek PRZEPRASZAM z metka 0 ZL - slowa nic nie kosztuja."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    A = int(255 * a)
    d.rounded_rectangle([CX - 300, 400, CX + 300, 600], radius=40, fill=(240, 240, 244, A))
    d.polygon([(CX - 200, 600), (CX - 140, 600), (CX - 230, 680)], fill=(240, 240, 244, A))
    f = f_anton(84)
    d.text((CX - szer(d, "PRZEPRASZAM", f) / 2, 445), "PRZEPRASZAM", font=f, fill=CIEMNY + (A,))
    czlowiek(d, CX - 250, 800, 70, BIEL, a)
    t1 = kt["czas_slowa"](p.get("slowo", "kosztują")) - kt["od"] - 0.15
    if t > t1:
        _metka_ceny(d, CX + 210, 690, "0 ZŁ", ZOLTY, wej(t, t1, 0.3), s=1.1)
        pigulka(d, CX, 960, "SŁOWA NIC NIE KOSZTUJĄ", f_anton(50), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({
    "pytanie_gwiazdki": scena_pytanie_gwiazdki, "podejrzane": scena_podejrzane, "krzywa_ocen": scena_krzywa_ocen,
    "pytanie_celowanie": scena_pytanie_celowanie, "zgadywane": scena_zgadywane, "moneta_koszt": scena_moneta_koszt,
    "pytanie_paczka": scena_pytanie_paczka, "tanie_slowa": scena_tanie_slowa,
})


# ---------------------------------------------------------------- l1: odreczna karteczka

def _karteczka(d, cx, cy, s, a, q=1.0, kat_linii=1.0):
    A = int(255 * a)
    w = 240 * s
    d.rectangle([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], fill=(255, 226, 92, A))
    d.polygon([(cx + w / 2 - 40 * s, cy + w / 2), (cx + w / 2, cy + w / 2 - 40 * s), (cx + w / 2, cy + w / 2)], fill=(220, 190, 60, A))
    for j in range(3):
        y = cy - w / 2 + 60 * s + j * 55 * s
        x0 = cx - w / 2 + 30 * s
        dl = (w - 70 * s) * min(1, max(0, q * 3 - j)) * (0.95 - 0.15 * j)
        if dl > 2:
            pts = [(x0 + k, y + 6 * s * math.sin(k / (9 * s) + j)) for k in range(0, int(dl), 4)]
            if len(pts) > 1:
                d.line(pts, fill=(40, 60, 140, A), width=max(2, int(5 * s)))


def scena_pytanie_karteczka(im, t, dl, p, kt):
    akc = kt["akcent"]
    dol = pytanie_u_gory(im, p["linie"], t, 1.0, akc)
    nak, d = warstwa()
    cy = dol + 320
    _paczka2(d, CX - 60, cy + 40, 1.6, 1.0, akc)
    _karteczka(d, CX + 170, cy - 20, 0.9, 1.0, q=0.4 + 0.6 * wej(t, 0.1, 1.2))
    im.alpha_composite(nak)


def scena_chwila(im, t, dl, p, kt):
    """Reka pisze karteczke - widac, ze ktos poswiecil klientowi chwile."""
    akc = kt["akcent"]
    nak, d = warstwa()
    a = wej(t, 0, 0.3)
    q = wej(t, 0.2, 2.0)
    _karteczka(d, CX, 600, 1.5, a, q=q)
    px = CX - 140 + 280 * ((q * 3) % 1)
    py = 520 + 82 * min(2, int(q * 3))
    d.line([px, py, px + 120, py - 160], fill=(30, 30, 36, int(255 * a)), width=18)
    t1 = kt["czas_slowa"](p.get("slowo", "chwilę")) - kt["od"] - 0.15
    if t > t1:
        pigulka(d, CX, 960, "KTOŚ POŚWIĘCIŁ CI CHWILĘ", f_anton(48), akc + (240,), CIEMNY + (255,))
    im.alpha_composite(nak)


s6.SCENY.update({"pytanie_karteczka": scena_pytanie_karteczka, "chwila": scena_chwila})
