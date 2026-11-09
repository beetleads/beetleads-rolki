#!/usr/bin/env python3
"""Zdjecie Unsplasha -> kadr Beetleads.

Sufit jasnosci jest ze skilla `zdjecia` (srednia L <= 90, inaczej kadr jest
plama). PODLOGA doszla 09.11: przy bardzo ciemnym zdjeciu ujecie pod scrimem
0,30 jest czarnym ekranem, czyli tym, co zalozyciel nazwal "puste bez efektow".

Gdzie dokladnie lezy ta podloga, sprawdzilem ARKUSZEM, a nie na wyczucie:
zlozylem dziewiec zdjec o L od 11 do 57 ze scrimem 0,30 i obejrzalem.
Przy L 16-26 temat zdjecia (sciana plakatow, sluchawki, biurko) jest nadal
czytelny; dopiero przy L okolo 10 zostaje czarna plama z jednym swiatlem.
Pierwsza wersja miala podloge 45 i kazala wymieniac polowe biblioteki -
to byl moj prog z sufitu, nie wynik pomiaru.

WAZNE: podloge trzymamy na ORYGINALE z Unsplasha, nigdy przez rozjasnianie
gotowego, juz przyciemnionego JPEG-a. Proba takiego ratunku 09.11 rozwalila
D1_2, C10_2 i P10_5 na zielono-czerwone pasy - w cieniach skompresowanego
pliku nie ma juz informacji do wyciagniecia.

Uzycie: python3 foto.py oryginal.jpg public/C1_2.jpg
"""
import sys, pathlib
import numpy as np
from PIL import Image, ImageEnhance

PODLOGA, CEL_DOL, CEL_GORA, SUFIT = 18.0, 26.0, 86.0, 90.0
SZER, WYS = 1400, 1789

def srednia(im):
    return float(np.asarray(im.convert("L")).mean())

def przygotuj(wej, wyj, srodek=0.35):
    im = Image.open(wej).convert("RGB")
    doc = SZER / WYS
    w, h = im.size
    if w / h > doc:
        nw = int(h * doc); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / doc); g = int((h - nh) * srodek)
        im = im.crop((0, g, w, g + nh))
    im = im.resize((SZER, WYS), Image.LANCZOS)

    L = srednia(im)
    if L > SUFIT:                      # za jasne - przyciemniamy
        for _ in range(12):
            im = ImageEnhance.Brightness(im).enhance(max(0.55, CEL_GORA / srednia(im)))
            if srednia(im) <= CEL_GORA:
                break
    elif L < PODLOGA:                  # za ciemne - wyciagamy cienie gamma na ORYGINALE
        a = np.asarray(im, dtype=np.float32) / 255.0
        lo, hi = 0.25, 1.0
        for _ in range(24):
            g = (lo + hi) / 2
            if srednia(Image.fromarray((np.power(a, g) * 255).astype(np.uint8))) < CEL_DOL:
                hi = g
            else:
                lo = g
        im = Image.fromarray((np.power(a, (lo + hi) / 2) * 255).astype(np.uint8))

    im.save(wyj, quality=92)
    k = srednia(im)
    stan = "OK" if PODLOGA <= k <= SUFIT else "POZA ZAKRESEM - nie uzywaj"
    return round(k, 1), stan

if __name__ == "__main__":
    L, stan = przygotuj(sys.argv[1], sys.argv[2])
    print(f"{pathlib.Path(sys.argv[2]).name}: L={L} {stan}")
