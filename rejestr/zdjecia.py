#!/usr/bin/env python3
"""Bramka zdjec rolek Beetleads - powtorzenia w kadrze.

09.11 wyszlo, ze te same pliki leza pod roznymi tematami: D3_4 i P10_1 to
jedno zdjecie, a mialy pojsc 11 i 12 listopada, dzien po dniu. Widz nie czyta
nazw plikow, tylko widzi ten sam kadr drugi dzien z rzedu - dokladnie zarzut
"ujecia dalej sa te same".

Sprawdza dwie rzeczy:
  - IDENTYCZNE pliki (md5) uzyte w wiecej niz jednym temacie,
  - PODOBNE kadry (hash percepcyjny, odleglosc Hamminga <= PROG) - to tylko
    OSTRZEZENIE do obejrzenia okiem, bo hash myli uklad jasnosci z trescia.

Sprawdza TYLKO zdjecia faktycznie wpisane do specyfikacji rolek
(dane/n/*.json, pole "foty") - plik lezacy w public/ i nieuzywany przez zadna
rolke nie jest powtorzeniem i nie ma po co o nim krzyczec.

Uzycie:
    python3 zdjecia.py /home/claude/silnik4
Kod wyjscia 1, gdy cokolwiek sie powtarza.
"""
import hashlib, json, pathlib, re, sys, collections
from PIL import Image

PROG = 6          # <= tyle bitow roznicy to dla oka ten sam kadr

def phash(p, bok=8):
    im = Image.open(p).convert("L").resize((bok * 4, bok * 4), Image.LANCZOS)
    import numpy as np
    a = np.asarray(im, dtype=float)
    d = np.fft.rfft2(a)[:bok, :bok]
    m = np.abs(d); med = sorted(m.flatten())[len(m.flatten()) // 2]
    return "".join("1" if v > med else "0" for v in m.flatten())

def uzyte(silnik):
    """{nazwa pliku: [kody rolek]} na podstawie specyfikacji, nie zawartosci public/."""
    mapa = collections.defaultdict(list)
    for spec in sorted((pathlib.Path(silnik) / "dane" / "n").glob("*.json")):
        if spec.stem.endswith("_slowa"):
            continue
        try:
            d = json.loads(spec.read_text(encoding="utf-8"))
        except Exception:
            continue
        for f in d.get("foty", []):
            if spec.stem not in mapa[f]:
                mapa[f].append(spec.stem)
    return dict(mapa)


def main(silnik):
    mapa = uzyte(silnik)
    pub = pathlib.Path(silnik) / "public"
    pliki = [pub / n for n in sorted(mapa) if (pub / n).exists()]
    if not pliki:
        print("brak zdjec w specyfikacjach - nie ma czego sprawdzac")
        return 0
    def temat(nazwa):
        return mapa.get(nazwa, [None])[0]
    # 09.11: pierwsza wersja pamietala tylko JEDEN temat na plik (setdefault), wiec
    # ta sama NAZWA wpisana do dwoch specyfikacji w ogole nie wchodzila do porownania.
    # Tak przeszlo D4_3.jpg - to samo ujecie w C5 (10.11) i D4 (17.11). Widz nie
    # odroznia "tego samego pliku" od "dwoch kopii tego samego zdjecia".
    ta_sama_nazwa = [(f, t_) for f, t_ in sorted(mapa.items()) if len(t_) > 1]
    md5 = collections.defaultdict(list)
    for p in pliki:
        md5[hashlib.md5(p.read_bytes()).hexdigest()].append(p.name)
    bledy, ostrzezenia = [], []
    for f, t_ in ta_sama_nazwa:
        bledy.append(("TA SAMA NAZWA", [f"{f} -> {', '.join(t_)}"]))
    for grupa in md5.values():
        tematy = {temat(n) for n in grupa}
        if len(tematy) > 1:
            bledy.append(("IDENTYCZNE", sorted(grupa)))
    hashe = {p.name: phash(p) for p in pliki}
    nazwy = list(hashe)
    for i, a in enumerate(nazwy):
        for b in nazwy[i + 1:]:
            if temat(a) == temat(b):
                continue
            if any(x[1] == sorted([a, b]) for x in bledy):
                continue
            d = sum(c1 != c2 for c1, c2 in zip(hashe[a], hashe[b]))
            if d <= PROG:
                ostrzezenia.append((f"PODOBNE({d})", [a, b]))
    # 09.11: hash percepcyjny liczy uklad jasnosci, nie tresc. C8_3 (korytarz
    # hotelowy) i L5_1 (szyny pustego regalu) wyszly na odleglosc 6, a dla widza
    # nie maja ze soba nic wspolnego. Identyczny plik to BLAD, bo tu nie ma czego
    # ogladac. Podobny kadr to OSTRZEZENIE do obejrzenia para obok pary - inaczej
    # bramka zaczyna kasowac dobre zdjecia i przestaje sie jej ufac.
    for typ, g in bledy + ostrzezenia:
        print(f"{typ}: {', '.join(g)}")
    print(f"\n{len(pliki)} zdjec, identycznych miedzy tematami: {len(bledy)}, "
          f"podobnych do obejrzenia: {len(ostrzezenia)}")
    return 1 if bledy else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/silnik4"))
