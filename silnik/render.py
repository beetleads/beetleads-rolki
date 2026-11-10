#!/usr/bin/env python3
"""Silnik 5 rolek Beetleads - rysowane sceny, bez przegladarki.

Powod istnienia: silnik 4 mial tylko cztery elementy (pigulka, karta, slupki,
ludzie) i przez wiekszosc rolki na ekranie zostawalo samo zdjecie z napisem.
Zalozyciel 10.11: "to nie wyglada jak wczesniejsze edycje". Tutaj kazda scena
jest rysowana, a zdjecie jest tylko przyciemnionym tlem.

Zasady z rolki referencyjnej (skill rolki-aip, sekcja 0b):
  - ujecie STOI, zmienia sie tylko na cieciu; nowe ujecie co ok. 1,6-2,2 s
  - kazde zdanie niesie element; scena-schemat na ciemnym tle przynajmniej raz
  - dwa akcenty: cyjan = mechanizm i liczby z badania, zolty = napisy i rada
  - @beetleads na kazdej klatce, napisy karaoke na linii oczu
  - czasy slow ZAWSZE z transkrypcji nagrania

Uzycie: python3 render.py spec.json wyjscie.mp4
"""
import json, math, subprocess, sys, pathlib, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
TLO = (14, 14, 17)
BIEL = (255, 255, 255)
CIEMNY = (23, 17, 13)
SAFE_L, SAFE_R = 224, 856
CAP_Y = 920
FONTY = pathlib.Path(__file__).parent / "fonty"


def f_anton(px):
    return ImageFont.truetype(str(FONTY / "Anton.ttf"), px)


def f_inter(px, waga="bold"):
    plik = "Inter-Bold.ttf" if waga == "bold" else "Inter-SemiBold.ttf"
    return ImageFont.truetype(str(FONTY / plik), px)


def hexkolor(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def szer(d, tekst, font):
    l, t, r, b = d.textbbox((0, 0), tekst, font=font)
    return r - l


# ---------------------------------------------------------------- tla

WEJSCIE = 0.42      # rozjazd okladki w pierwsza scene
PRZENIKANIE = 0.26  # dlugosc przenikania miedzy ujeciami
MARGINES = 0.17   # zapas na jazde kadru wewnatrz ujecia


def tlo_foto(plik, kadr):
    """Zdjecie jako przyciemnione tlo, w rozmiarze z zapasem - okno jedzie wewnatrz
    ujecia (patrz `okno`). 10.11: w referencji tylko 1% klatek nie ma ruchu, wiec
    kadr nie moze stac ani sekundy."""
    im = Image.open(plik).convert("RGB")
    zoom = [1.00, 1.06, 1.03, 1.08][kadr % 4]
    dx = [0, -0.03, 0.03, 0][kadr % 4]
    dy = [0, 0.02, -0.02, 0.01][kadr % 4]
    sk = max(W / im.width, H / im.height) * zoom * (1 + MARGINES)
    im = im.resize((int(im.width * sk) + 1, int(im.height * sk) + 1), Image.LANCZOS)
    x = int((im.width - W) / 2 + dx * W)
    y = int((im.height - H) / 2 + dy * H)
    x = max(0, min(x, im.width - W))
    y = max(0, min(y, im.height - H))
    WW, HH = int(W * (1 + MARGINES)), int(H * (1 + MARGINES))
    x = max(0, min(x, im.width - WW))
    y = max(0, min(y, im.height - HH))
    im = im.crop((x, y, x + WW, y + HH))
    # przyciemnienie zalezne od jasnosci zdjecia - jasne kadry gasimy mocniej,
    # zeby rysowane elementy i napisy byly czytelne na kazdym tle
    import numpy as _np
    jasnosc = float(_np.array(im.convert("L").resize((40, 40))).mean())
    alfa = min(0.78, max(0.45, 0.35 + (jasnosc - 60) / 255 * 0.75))
    szkic = Image.new("RGB", (WW, HH), TLO)
    return Image.blend(im, szkic, alfa)


def tlo_desen(akcent, ziarno=7):
    """Ciemne tlo z deseniem - scena-schemat z rolki referencyjnej. Tez nadwymiarowe,
    zeby desen plynal w poprzek kadru zamiast stac."""
    WW, HH = int(W * (1 + MARGINES)), int(H * (1 + MARGINES))
    im = Image.new("RGB", (WW, HH), TLO)
    d = ImageDraw.Draw(im)
    rnd = random.Random(ziarno)
    kol = tuple(int(c * 0.22) for c in akcent)
    for _ in range(34):
        x = rnd.randint(-100, WW)
        y = rnd.randint(-100, HH)
        punkty = []
        for i in range(26):
            punkty.append((x + i * 26, y + int(44 * math.sin(i / 2.4 + rnd.random()))))
        d.line(punkty, fill=kol, width=3, joint="curve")
    return im


def okno(baza, post, dlugosc, kierunek):
    """Wycina kadr 1080x1920 z nadwymiarowego tla; okno jedzie przez cale ujecie.
    Ruch jest powolny (caly przejazd to ok. 2% szerokosci na sekunde) - ma oddychac,
    nie wozic widzem."""
    zap_x, zap_y = baza.width - W, baza.height - H
    p = min(1, max(0, post / max(dlugosc, 0.1)))
    p = p * p * (3 - 2 * p)            # wygladzenie koncow, zeby ciecie nie szarpalo
    kx, ky = kierunek
    x = int(zap_x * (0.5 + kx * (p - 0.5) * 0.42))
    y = int(zap_y * (0.5 + ky * (p - 0.5) * 0.42))
    return baza.crop((x, y, x + W, y + H))


# ---------------------------------------------------------------- elementy

def pigulka(d, srodek_x, y, tekst, font, tlo_k, tekst_k, obrys=None, pad=(26, 14), r=None):
    w = szer(d, tekst, font) + pad[0] * 2
    h = font.size + pad[1] * 2
    x0 = srodek_x - w // 2
    r = r if r is not None else h // 2
    d.rounded_rectangle([x0, y, x0 + w, y + h], radius=r, fill=tlo_k,
                        outline=obrys, width=3 if obrys else 0)
    d.text((x0 + pad[0], y + pad[1] - font.size * 0.08), tekst, font=font, fill=tekst_k)
    return (x0, y, x0 + w, y + h)


def el_chip(im, d, el, akcent, post):
    font = f_inter(32, "semi")
    t = el["tekst"].upper()
    y = el.get("y", 120) + int(3 * math.sin(post * 2.0))
    a = int(255 * min(1, post / 0.18))
    nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nak)
    pigulka(dn, W // 2, y, t, font, (14, 14, 17, 225), akcent + (a,), obrys=akcent + (a,))
    im.alpha_composite(nak)


def el_slupki(im, d, el, akcent, cyjan, post):
    """Porownanie A/B: dwa slupki z etykietami, wygrany w cyjanie."""
    y = el.get("y", 300)
    kolumny = el.get("kolumny") or [el["a"], el["b"]]
    maks = max([k["wartosc"] for k in kolumny] + [1])
    wys = 380                      # 10.11: elementy maja byc wyrazniej widoczne
    szer_s = 150 if len(kolumny) > 2 else 180
    luz = 48 if len(kolumny) > 2 else 150
    szer_calk = len(kolumny) * szer_s + (len(kolumny) - 1) * luz
    x0 = W // 2 - szer_calk // 2
    wejscie = min(1, post / 0.35)
    kolory = [cyjan, (150, 150, 158), (110, 110, 118)]
    for i, dane in enumerate(kolumny):
        kol = hexkolor(dane["kolor"]) if dane.get("kolor") else kolory[min(i, 2)]
        x = x0 + i * (szer_s + luz)
        h = int(wys * dane["wartosc"] / maks * wejscie)
        d.rounded_rectangle([x, y + wys - h, x + szer_s, y + wys], radius=14, fill=kol)
        d.rounded_rectangle([x, y, x + szer_s, y + wys], radius=14, outline=(90, 90, 96), width=3)
        font = f_inter(24 if len(kolumny) > 2 else 30, "semi")
        pigulka(d, x + szer_s // 2, y + wys + 18, dane["etykieta"].upper(), font,
                (14, 14, 17), BIEL, obrys=kol, pad=(14, 10))
        if dane.get("liczba"):
            fa = f_anton(64)
            cel = dane["liczba"]
            if cel.rstrip("%").isdigit():
                biezaca = int(int(cel.rstrip("%")) * min(1, post / 0.7))
                tekst = f"{biezaca}%" if cel.endswith("%") else str(biezaca)
            else:
                tekst = cel
            uniesienie = int(4 * math.sin(post * 2.6 + i))
            d.text((x + szer_s // 2 - szer(d, tekst, fa) // 2, y - 68 - uniesienie),
                   tekst, font=fa, fill=kol)


def el_ludzie(im, d, el, akcent, cyjan, post):
    """Siatka ikonek ludzi - proba badania; zaznaczone w cyjanie."""
    y = el.get("y", 320)
    ile = el["ile"]
    zazn = el.get("zaznaczone", 0)
    kol_w = 10
    krok = 70
    x0 = W // 2 - (kol_w * krok) // 2 + 10
    widoczne = int(ile * min(1, post / 0.5))
    for i in range(widoczne):
        cx = x0 + (i % kol_w) * krok
        cy = y + (i // kol_w) * 74
        if i < zazn:
            j = 0.7 + 0.3 * math.sin(post * 3.0 + i * 0.35)
            kol = tuple(int(c * j) for c in cyjan)
        else:
            kol = (170, 170, 178)
        d.ellipse([cx - 14, cy - 28, cx + 14, cy], outline=kol, width=4)
        d.arc([cx - 23, cy - 2, cx + 23, cy + 42], 180, 360, fill=kol, width=4)
    if el.get("podpis"):
        font = f_inter(30, "semi")
        wiersze = (ile + kol_w - 1) // kol_w
        pigulka(d, W // 2, y + wiersze * 74 + 18, el["podpis"].upper(), font,
                (14, 14, 17), BIEL, obrys=cyjan)


def el_schemat(im, d, el, akcent, cyjan, post):
    """Rysunek mechanizmu: dwa wezly polaczone kropkami (jak oko-kubek w referencji)."""
    y = el.get("y", 430)
    lx, rx = W // 2 - 230, W // 2 + 230
    d.ellipse([lx - 88, y - 56, lx + 88, y + 56], outline=BIEL, width=6)
    d.ellipse([lx - 26, y - 26, lx + 26, y + 26], fill=BIEL)
    for i in range(6):
        faza = (post * 0.8 + i / 6.0) % 1.0
        x = lx + 100 + faza * 260
        r = 7 + 4 * math.sin(faza * math.pi)
        jas = 0.45 + 0.55 * math.sin(faza * math.pi)
        kol = tuple(int(c * jas) for c in cyjan)
        d.ellipse([x - r, y - r, x + r, y + r], fill=kol)
    d.rounded_rectangle([rx - 76, y - 66, rx + 76, y + 66], radius=24, outline=cyjan, width=6)
    if el.get("etykieta"):
        pigulka(d, rx, y - 140, el["etykieta"].upper(), f_inter(28, "semi"), cyjan, CIEMNY)
    if el.get("podpis"):
        pigulka(d, lx, y - 140, el["podpis"].upper(), f_inter(28, "semi"), (14, 14, 17), BIEL, obrys=BIEL)


def el_karta_liczby(im, d, el, akcent, cyjan, post):
    """Ciemna karta z liczba z badania - 'POLICZONE W BADANIU'."""
    y = el.get("y", 1180)
    wejscie = min(1, post / 0.3)
    fn = f_inter(28, "semi")
    f1 = f_anton(80)
    f2 = f_anton(80)
    linie = [(el["l1"], BIEL, f1)] + ([(el["l2"], cyjan, f2)] if el.get("l2") else [])
    w = max([szer(d, t, f) for t, _, f in linie] + [szer(d, el["naglowek"], fn)]) + 110
    w = min(w, SAFE_R - SAFE_L + 60)
    h = 72 + sum(f.size + 14 for _, _, f in linie)
    x0 = W // 2 - w // 2
    y0 = y - int((1 - wejscie) * 24)
    nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nak)
    dn.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=18,
                         fill=(10, 12, 16, int(238 * wejscie)), outline=cyjan + (int(255 * wejscie),), width=3)
    puls = 0.75 + 0.25 * math.sin(post * 3.4)
    dn.rounded_rectangle([x0 - 3, y0 - 3, x0 + w + 3, y0 + h + 3], radius=21,
                         outline=cyjan + (int(70 * puls * wejscie),), width=2)
    kreska = 20 + 12 * math.sin(post * 2.2)
    dn.line([W // 2 - kreska, y0 + 20, W // 2 + kreska, y0 + 20], fill=cyjan + (255,), width=4)
    dn.text((W // 2 - szer(dn, el["naglowek"].upper(), fn) // 2, y0 + 30),
            el["naglowek"].upper(), font=fn, fill=(190, 195, 205, int(255 * wejscie)))
    yy = y0 + 66
    for t, kol, f in linie:
        dn.text((W // 2 - szer(dn, t.upper(), f) // 2, yy), t.upper(), font=f,
                fill=kol + (int(255 * wejscie),))
        yy += f.size + 14
    im.alpha_composite(nak)


def el_domkniecie(im, d, el, akcent, cyjan, post):
    """Karta wniosku 'ZROB TO U SIEBIE' - druga linia w akcencie."""
    y = el.get("y", 1240)
    wejscie = min(1, post / 0.3)
    fn = f_inter(26, "semi")
    f1 = f_anton(64)
    linie = [(el["l1"], BIEL), (el.get("l2", ""), akcent)]
    linie = [(t, k) for t, k in linie if t]
    w = max([szer(d, t.upper(), f1) for t, _ in linie]) + 110
    h = 70 + len(linie) * (f1.size + 12)
    x0 = W // 2 - w // 2
    nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nak)
    dn.rounded_rectangle([x0, y, x0 + w, y + h], radius=16,
                         fill=(12, 10, 8, int(240 * wejscie)), outline=akcent + (int(255 * wejscie),), width=3)
    dn.line([W // 2 - 24, y + 20, W // 2 + 24, y + 20], fill=akcent + (255,), width=4)
    dn.text((W // 2 - szer(dn, el["naglowek"].upper(), fn) // 2, y + 28),
            el["naglowek"].upper(), font=fn, fill=(200, 196, 190, int(255 * wejscie)))
    yy = y + 62
    for t, kol in linie:
        dn.text((W // 2 - szer(dn, t.upper(), f1) // 2, yy), t.upper(), font=f1,
                fill=kol + (int(255 * wejscie),))
        yy += f1.size + 12
    im.alpha_composite(nak)
    if post > 0.5:
        szer_l = int(min(1, (post - 0.5) / 0.4) * 200)
        d.line([W // 2 - szer_l // 2, y + h + 22, W // 2 + szer_l // 2, y + h + 22],
               fill=akcent, width=6)


def el_zapamietaj(im, d, el, akcent, post):
    font = f_inter(30, "semi")
    puls = 1 + 0.04 * math.sin(post * 7)
    f = f_inter(int(30 * puls), "semi")
    pigulka(d, W // 2, el.get("y", 120), "ZAPAMIĘTAJ", f, (14, 14, 17), BIEL, obrys=akcent, r=12)


def el_tak_nie(im, d, el, akcent, cyjan, post):
    """Ptaszek i krzyzyk - domkniecie rady, jak w rolkach wzorcowych."""
    y = el.get("y", 300)
    wejscie = min(1, post / 0.3)
    bok = 150
    for i, (dobry, kol) in enumerate([(True, akcent), (False, (120, 120, 128))]):
        x = W // 2 - bok - 30 + i * (bok + 60)
        skok = int(6 * math.sin(post * 3.0 + i * 1.6)) if dobry else 0
        d.rounded_rectangle([x, y - skok, x + bok, y + bok - skok], radius=22,
                            fill=kol if dobry else (34, 34, 38))
        cx, cy = x + bok // 2, y + bok // 2 - skok
        if dobry:
            d.line([cx - 26, cy, cx - 6, cy + 22], fill=CIEMNY, width=10)
            d.line([cx - 6, cy + 22, cx + 28, cy - 22], fill=CIEMNY, width=10)
        else:
            d.line([cx - 20, cy - 20, cx + 20, cy + 20], fill=(150, 150, 158), width=9)
            d.line([cx + 20, cy - 20, cx - 20, cy + 20], fill=(150, 150, 158), width=9)
    if el.get("podpis"):
        pigulka(d, W // 2, y + bok + 28, el["podpis"].upper(), f_inter(28, "semi"),
                (14, 14, 17), BIEL, obrys=akcent)


def el_karty(im, d, el, akcent, cyjan, post):
    """Dwie karty obok siebie z wartosciami - ilustracja hooka. 10.11: pierwsze
    sekundy maja najwiecej uwagi, a pas gorny byl w nich pusty."""
    y = el.get("y", 300)
    wejscie = min(1, post / 0.4)
    bok_w, bok_h, luz = 300, 340, 60
    x0 = W // 2 - bok_w - luz // 2
    for i, karta in enumerate(el["karty"]):
        wygrany = karta.get("wygrany")
        kol = (akcent if wygrany else cyjan) if karta.get("akcent", True) else (150, 150, 158)
        x = x0 + i * (bok_w + luz)
        skok = int(8 * math.sin(post * 2.6 + i * 1.5)) * (1 if wygrany else 0)
        yy = y - skok - int((1 - wejscie) * 20)
        d.rounded_rectangle([x, yy, x + bok_w, yy + bok_h], radius=26,
                            fill=(16, 16, 20), outline=kol, width=5)
        fa = f_anton(100)
        t = karta["wartosc"]
        while szer(d, t, fa) > bok_w - 36 and fa.size > 40:
            fa = f_anton(fa.size - 4)
        d.text((x + bok_w // 2 - szer(d, t, fa) // 2, yy + bok_h // 2 - fa.size // 2 - 10),
               t, font=fa, fill=kol)
        pigulka(d, x + bok_w // 2, yy + bok_h + 20, karta["etykieta"].upper(),
                f_inter(28, "semi"), (14, 14, 17), BIEL, obrys=kol, pad=(18, 12))
    # znak zapytania miedzy kartami - pytanie hooka
    fq = f_anton(76)
    puls = 1 + 0.06 * math.sin(post * 4.0)
    fq = f_anton(int(76 * puls))
    d.text((W // 2 - szer(d, "?", fq) // 2, y + bok_h // 2 - fq.size // 2), "?",
           font=fq, fill=akcent)


def el_tabliczka(im, d, el, akcent, cyjan, post):
    """Tabliczka ostrzegawcza z wnioskiem marketingowym - zolty trojkat z wykrzyknikiem
    i napis, zeby na koncu bylo wiadomo, co z tego wynika dla firmy."""
    y = el.get("y", 130)
    wejscie = min(1, post / 0.3)
    font = f_inter(34, "bold")
    t = el.get("tekst", "Wniosek marketingowy").upper()
    w = szer(d, t, font) + 150
    h = 86
    x0 = W // 2 - w // 2
    puls = 0.6 + 0.4 * abs(math.sin(post * 2.4))
    nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nak)
    dn.rounded_rectangle([x0, y, x0 + w, y + h], radius=16,
                         fill=(14, 14, 17, int(238 * wejscie)),
                         outline=akcent + (int(255 * wejscie),), width=4)
    dn.rounded_rectangle([x0 - 4, y - 4, x0 + w + 4, y + h + 4], radius=20,
                         outline=akcent + (int(90 * puls * wejscie),), width=2)
    tx, ty = x0 + 34, y + h // 2
    dn.polygon([(tx, ty + 22), (tx + 44, ty + 22), (tx + 22, ty - 24)],
               fill=akcent + (int(255 * wejscie),))
    fw = f_anton(30)
    dn.text((tx + 22 - szer(dn, "!", fw) // 2, ty - 16), "!", font=fw, fill=CIEMNY + (255,))
    dn.text((x0 + 104, y + h // 2 - font.size // 2 - 2), t, font=font,
            fill=BIEL + (int(255 * wejscie),))
    im.alpha_composite(nak)


def el_follow(im, d, el, akcent, cyjan, post):
    """Przycisk OBSERWUJ z kursorem, ktory najezdza i klika. Klikniecie wypada
    w `klik` sekundy od wejscia - dzwiek klikniecia miksowany jest w tej samej chwili."""
    y = el.get("y", 330)
    klik = el.get("klik", 0.9)
    wejscie = min(1, post / 0.25)
    po = post > klik
    w, h = 530, 140
    x0 = W // 2 - w // 2
    wcisniety = 1.0 if not (klik - 0.07 < post < klik + 0.12) else 0.94
    ww, hh = int(w * wcisniety), int(h * wcisniety)
    x, yy = W // 2 - ww // 2, y + (h - hh) // 2
    tlo_p = akcent if not po else (26, 26, 30)
    d.rounded_rectangle([x, yy, x + ww, yy + hh], radius=hh // 2, fill=tlo_p,
                        outline=akcent, width=4)
    font = f_inter(46, "bold")
    t = "OBSERWUJ" if not po else "OBSERWUJESZ"
    kol = CIEMNY if not po else akcent
    d.text((W // 2 - szer(d, t, font) // 2 + (16 if po else 0),
            yy + hh // 2 - font.size // 2 - 2), t, font=font, fill=kol)
    if po:
        cx, cy = W // 2 - szer(d, t, font) // 2 - 26, yy + hh // 2
        d.line([cx - 16, cy, cx - 4, cy + 12], fill=akcent, width=7)
        d.line([cx - 4, cy + 12, cx + 18, cy - 14], fill=akcent, width=7)
    # pierscien po klikniecu
    if 0 < post - klik < 0.45:
        r = int(90 + 190 * (post - klik) / 0.45)
        a = int(190 * (1 - (post - klik) / 0.45))
        nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dn = ImageDraw.Draw(nak)
        dn.ellipse([W // 2 - r, y + h // 2 - r, W // 2 + r, y + h // 2 + r],
                   outline=akcent + (a,), width=5)
        im.alpha_composite(nak)
    # kursor: najezdza na przycisk i zostaje
    p = min(1, post / max(klik, 0.01))
    kx = int(W // 2 + 250 - 250 * p)
    ky = int(y + h + 150 - 110 * p)
    d.polygon([(kx, ky), (kx, ky + 46), (kx + 13, ky + 34), (kx + 22, ky + 52),
               (kx + 32, ky + 47), (kx + 23, ky + 29), (kx + 38, ky + 27)], fill=BIEL)
    if el.get("podpis"):
        pigulka(d, W // 2, y + h + 34, el["podpis"].upper(), f_inter(26, "semi"),
                (14, 14, 17), BIEL, obrys=akcent)


WYSOKOSCI = {"chip": 90, "karty": 420, "slupki": 520, "ludzie": 500, "schemat": 300,
             "karta_liczby": 290, "domkniecie": 290, "zapamietaj": 90, "tak_nie": 230,
             "follow": 240, "tabliczka": 110, "lista": 430}


def bramka_kolizji(spec):
    """Czy w tej samej sekundzie dwa elementy nie nachodza na siebie w pionie.
    Napisy maja wlasny pas (CAP_Y +/- 110) i tez sa sprawdzane."""
    el = [(e, e.get("y", 300), e.get("y", 300) + WYSOKOSCI.get(e["typ"], 200))
          for e in spec["elementy"]]
    el.append(({"typ": "napisy", "od": 0, "do": spec["dlugosc"]}, CAP_Y - 110, CAP_Y + 110))
    zle = []
    for i in range(len(el)):
        a, a0, a1 = el[i]
        for b, b0, b1 in el[i + 1:]:
            if a["od"] < b["do"] - 0.05 and b["od"] < a["do"] - 0.05 and a0 < b1 and b0 < a1:
                zle.append(f'{a["typ"]} x {b["typ"]} ({max(a["od"], b["od"]):.1f} s)')
    return zle


def el_lista(im, d, el, akcent, cyjan, post):
    """Trzy pozycje listy z wyroznieniem jednej - animacja wniosku pokazuje to,
    o czym mowi lektor (cennik, warianty, kolejnosc cen, rodzaj gratisu).
    10.11: "jak dajesz wniosek, to animacja przedstawia to, o czym mowisz"."""
    y = el.get("y", 300)
    poz = el["pozycje"]
    wybrany = el.get("wybrany", 1)
    wiersz_h, luz = 104, 20
    szer_l = 660
    x0 = W // 2 - szer_l // 2
    for i, tekst in enumerate(poz):
        wejscie = min(1, max(0, (post - i * 0.18) / 0.3))
        if wejscie <= 0:
            continue
        yy = y + i * (wiersz_h + luz)
        akt = i == wybrany and post > len(poz) * 0.18 + 0.2
        puls = 1 + 0.03 * math.sin(post * 3.4) if akt else 1
        przes = int((1 - wejscie) * 40)
        kol = akcent if akt else (120, 120, 128)
        h = int(wiersz_h * puls)
        d.rounded_rectangle([x0 + przes, yy, x0 + szer_l + przes, yy + h], radius=20,
                            fill=(18, 18, 22) if not akt else (26, 22, 10),
                            outline=kol, width=5 if akt else 3)
        f = f_inter(36, "bold" if akt else "semi")
        while szer(d, tekst.upper(), f) > szer_l - 140 and f.size > 22:
            f = f_inter(f.size - 2, "bold" if akt else "semi")
        d.text((x0 + 48 + przes, yy + h // 2 - f.size // 2 - 2), tekst.upper(), font=f,
               fill=BIEL if akt else (170, 170, 178))
        if akt:
            cx = x0 + szer_l - 56 + przes
            cy = yy + h // 2
            d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=akcent)
            d.line([cx - 12, cy, cx - 3, cy + 10], fill=CIEMNY, width=7)
            d.line([cx - 3, cy + 10, cx + 13, cy - 11], fill=CIEMNY, width=7)
    if el.get("podpis"):
        pigulka(d, W // 2, y + len(poz) * (wiersz_h + luz) + 8, el["podpis"].upper(),
                f_inter(28, "semi"), (14, 14, 17), BIEL, obrys=akcent)


def bramka_pasow(spec):
    """Trzy pasy maja byc zajete przez caly czas: ilustracja u gory, napis na
    srodku, ciemna karta na dole. 10.11 zalozyciel pokazal cztery rolki wzorcowe -
    w kazdej gora i dol sa zajete niemal caly czas, a moja wersja miala je puste."""
    gora = [e for e in spec["elementy"] if e.get("y", 300) < 760]
    dol = [e for e in spec["elementy"] if e.get("y", 300) >= 1000]
    braki = []
    for pas, lista in (("gora", gora), ("dol", dol)):
        t = spec.get("okladka_do", 0.1)
        for e in sorted(lista, key=lambda e: e["od"]):
            if e["od"] > t + 0.45:
                braki.append(f"{pas}: pusto {t:.1f}-{e['od']:.1f} s")
            t = max(t, e["do"])
        if spec["dlugosc"] - 0.2 > t + 0.45:
            braki.append(f"{pas}: pusto {t:.1f}-{spec['dlugosc']:.1f} s")
    return braki


RYSUNKI = {
    "chip": el_chip, "slupki": el_slupki, "ludzie": el_ludzie, "schemat": el_schemat,
    "karta_liczby": el_karta_liczby, "domkniecie": el_domkniecie, "zapamietaj": el_zapamietaj,
    "tak_nie": el_tak_nie, "karty": el_karty, "lista": el_lista, "tabliczka": el_tabliczka, "follow": el_follow,
}


# ---------------------------------------------------------------- napisy

def grupy_slow(slowa, maks=5):
    """Grupa konczy sie na kropce, pytajniku albo pauzie w glosie - inaczej napis
    sklada slowa z dwoch zdan i czyta sie jak belkot (10.11: "Wiesz dlaczego? Stala kwota")."""
    g, biez = [], []
    for i, s in enumerate(slowa):
        biez.append(s)
        koniec_zdania = s["s"].rstrip()[-1:] in ".?!:"
        pauza = i + 1 < len(slowa) and slowa[i + 1]["od"] - s["do"] > 0.28
        if koniec_zdania or pauza or len(biez) == maks:
            g.append(biez)
            biez = []
    if biez:
        g.append(biez)
    return g


def rysuj_napisy(im, d, grupa, t, akcent):
    font = f_inter(46, "bold")   # 10.11: zalozyciel poprosil o troche wieksze napisy
    odstep = 16
    wiersze, biez, szer_b = [], [], 0
    for s in grupa:
        w = szer(d, s["s"], font) + 28
        if szer_b + w > SAFE_R - SAFE_L and biez:
            wiersze.append(biez)
            biez, szer_b = [], 0
        biez.append(s)
        szer_b += w + odstep
    if biez:
        wiersze.append(biez)
    y = CAP_Y - (len(wiersze) * (font.size + 34)) // 2
    nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nak)
    for wiersz in wiersze:
        szer_w = sum(szer(dn, s["s"], font) + 28 + odstep for s in wiersz) - odstep
        x = W // 2 - szer_w // 2
        for s in wiersz:
            w = szer(dn, s["s"], font) + 28
            mowione = s["od"] <= t <= s["do"]
            if mowione:
                dn.rounded_rectangle([x, y, x + w, y + font.size + 22], radius=10, fill=akcent + (255,))
                kol = CIEMNY + (255,)
            else:
                dn.rounded_rectangle([x, y, x + w, y + font.size + 22], radius=10, fill=(14, 14, 17, 205))
                kol = (255, 255, 255, 255)
            dn.text((x + 14, y + 6), s["s"], font=font, fill=kol)
            x += w + odstep
        y += font.size + 34
    im.alpha_composite(nak)


def znak_wodny(im, d):
    font = f_inter(22, "semi")
    t = "@beetleads"
    nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nak)
    dn.text((W // 2 - szer(dn, t, font) // 2, 1760), t, font=font, fill=(255, 255, 255, 150))
    im.alpha_composite(nak)


def okladka(spec, akcent):
    o = spec["okladka"]
    im = Image.open(o["foto"]).convert("RGB")
    sk = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * sk) + 1, int(im.height * sk) + 1), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, 0, (im.width - W) // 2 + W, H))
    im = Image.blend(im, Image.new("RGB", (W, H), TLO), 0.42).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1000, W, H], fill=(14, 14, 17, 225))
    y = 1060
    for i, linia in enumerate([o["l1"], o["l2"]]):
        f = f_anton(104)
        while szer(d, linia.upper(), f) > SAFE_R - SAFE_L + 120 and f.size > 60:
            f = f_anton(f.size - 4)
        kol = akcent if i == 1 else BIEL
        d.text((W // 2 - szer(d, linia.upper(), f) // 2, y), linia.upper(), font=f, fill=kol)
        y += f.size + 18
    znak_wodny(im, d)
    return im


# ---------------------------------------------------------------- montaz

def renderuj(spec_plik, wyjscie):
    spec = json.loads(pathlib.Path(spec_plik).read_text())
    akcent = hexkolor(spec.get("akcent", "#FFD84D"))
    cyjan = hexkolor(spec.get("cyjan", "#35D0E8"))
    dlugosc = spec["dlugosc"]
    klatki = int(round(dlugosc * FPS))
    braki = bramka_pasow(spec)
    if braki:
        print("BRAMKA PASOW - puste miejsca:", "; ".join(braki))
    kol = bramka_kolizji(spec)
    if kol:
        print("BRAMKA KOLIZJI - elementy nachodza:", "; ".join(kol))
    katalog = pathlib.Path(wyjscie).parent / ("kl_" + pathlib.Path(wyjscie).stem)
    katalog.mkdir(parents=True, exist_ok=True)

    # tla ujec licz RAZ - w srodku ujecia kadr i tak stoi
    bazy = []
    for i, u in enumerate(spec["ujecia"]):
        t = u["tlo"]
        if t["typ"] == "foto":
            bazy.append(tlo_foto(t["plik"], t.get("kadr", i)).convert("RGBA"))
        else:
            bazy.append(tlo_desen(cyjan, t.get("ziarno", 7 + i)).convert("RGBA"))

    okl = okladka(spec, akcent)
    grupy = grupy_slow(spec["slowa"])

    for k in range(klatki):
        t = k / FPS
        okl_do = spec.get("okladka_do", 0.1)
        if t < okl_do or t > dlugosc - 0.1:
            okl.convert("RGB").save(katalog / f"k{k:05d}.jpg", quality=93)
            continue
        idx = 0
        for i, u in enumerate(spec["ujecia"]):
            if u["od"] <= t < u["do"]:
                idx = i
                break
        u = spec["ujecia"][idx]
        kier = [(1, 0.3), (-1, -0.3), (0.4, 1), (-0.4, -1)][idx % 4]
        im = okno(bazy[idx], t - u["od"], u["do"] - u["od"], kier).copy()
        # 10.11: w rolkach wzorcowych ujecia PRZENIKAJA sie; twarde ciecie
        # rozrywa material na slajdy
        if idx > 0 and t - u["od"] < PRZENIKANIE:
            pop = spec["ujecia"][idx - 1]
            kier_p = [(1, 0.3), (-1, -0.3), (0.4, 1), (-0.4, -1)][(idx - 1) % 4]
            poprz = okno(bazy[idx - 1], pop["do"] - pop["od"], pop["do"] - pop["od"], kier_p)
            im = Image.blend(poprz, im, (t - u["od"]) / PRZENIKANIE)
        d = ImageDraw.Draw(im)
        for el in spec["elementy"]:
            if el["od"] <= t <= el["do"]:
                post = t - el["od"]
                fn = RYSUNKI[el["typ"]]
                if el["typ"] in ("chip",):
                    fn(im, d, el, akcent, post)
                elif el["typ"] == "zapamietaj":
                    fn(im, d, el, akcent, post)
                else:
                    fn(im, d, el, akcent, cyjan, post)
        # WEJSCIE Z OKLADKI (10.11): okladka rozjezdza sie w pierwsza scene -
        # start nie moze byc "nic sie nie dzieje", musi byc czym przykryty
        if t < okl_do + WEJSCIE:
            p = (t - okl_do) / WEJSCIE
            sk = 1 + 0.10 * (1 - p)
            pow = okl.resize((int(W * sk), int(H * sk)), Image.BILINEAR)
            pow = pow.crop(((pow.width - W) // 2, (pow.height - H) // 2,
                            (pow.width - W) // 2 + W, (pow.height - H) // 2 + H))
            pow = pow.filter(ImageFilter.GaussianBlur(10 * p))
            im = Image.blend(im, pow, max(0.0, 1 - p))
            d = ImageDraw.Draw(im)
            poz = int(220 * (1 - p))
            nak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dn = ImageDraw.Draw(nak)
            dn.line([0, 0, W, 0], fill=akcent + (0,), width=1)
            dn.rectangle([0, CAP_Y - 300 - poz, W, CAP_Y - 296 - poz],
                         fill=akcent + (int(230 * (1 - p)),))
            dn.rectangle([0, CAP_Y + 296 + poz, W, CAP_Y + 300 + poz],
                         fill=akcent + (int(230 * (1 - p)),))
            im.alpha_composite(nak)

        for g in grupy:
            if g[0]["od"] - 0.12 <= t <= g[-1]["do"] + 0.3:
                rysuj_napisy(im, d, g, t, akcent)
                break
        znak_wodny(im, d)
        im.convert("RGB").save(katalog / f"k{k:05d}.jpg", quality=93)

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
        "-i", str(katalog / "k%05d.jpg"), "-i", spec["audio"],
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
        "-g", "60", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        "-shortest", wyjscie], check=True)
    for p in katalog.glob("*.jpg"):
        p.unlink()
    katalog.rmdir()
    print("gotowe:", wyjscie, klatki, "klatek")


if __name__ == "__main__":
    renderuj(sys.argv[1], sys.argv[2])
