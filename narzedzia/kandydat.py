#!/usr/bin/env python3
"""Czy kandydat na zdjecie nie powtarza kadru - SPRAWDZANE PRZED wejsciem do public/.

09.11, wersja 1: bramka zdjecia.py lapala kolizje dopiero po wlozeniu pliku do
public/ i po pelnym ogledzie. Jeden kandydat przeszedl caly cykl i wylecial na
odleglosci 6 do trzech plikow naraz - stracony cykl.

09.11, wersja 2 (BLAD WERSJI 1): hash liczony z pliku SUROWEGO nie zgadza sie z
hashem z public/, bo foto.py zmienia kadr (na 1400x1789) i jasnosc. Kandydat
VNQ87bRNs5o mial na surowo odleglosc 8 ("ok"), a po foto.py spadl do 4 - czyli
dokladnie to, przed czym ta bramka ma chronic, przez nia przeszlo. Teraz skrypt
sam puszcza kandydata przez foto.py do pliku tymczasowego i hashuje WYNIK.

Uzycie:
    python3 kandydat.py /sciezka/do/surowego.jpg [kolejny.jpg ...]
    python3 kandydat.py --surowy gotowy_z_public.jpg     # bez foto.py
    python3 kandydat.py --pomin P5_ P11_ kandydat.jpg    # pomin wlasne stare pliki

Odleglosc <= 6 = dla oka ten sam kadr, nie bierz. 7-9 = obejrzyj pare obok pary.
"""
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from zdjecia import phash, uzyte

PROG = 6
SILNIK = "/home/claude/silnik4"


def przez_foto(zrodlo, kat):
    """foto.py robi kadr 1400x1789 i poprawia jasnosc - hash liczymy z WYNIKU."""
    wyj = pathlib.Path(kat) / (pathlib.Path(zrodlo).stem + "_tmp.jpg")
    r = subprocess.run([sys.executable, "-I", "foto.py", str(zrodlo), str(wyj)],
                       cwd=SILNIK, capture_output=True, text=True)
    if r.returncode != 0 or not wyj.exists():
        return None, (r.stdout + r.stderr).strip().splitlines()[-1:] or ["foto.py nie zrobil pliku"]
    return wyj, None


def main(argv):
    surowy = False
    pomin = []
    while argv and argv[0].startswith("--"):
        if argv[0] == "--surowy":
            surowy = True
            argv = argv[1:]
        elif argv[0] == "--pomin":
            argv = argv[1:]
            while argv and not argv[0].lower().endswith((".jpg", ".jpeg", ".png")):
                pomin.append(argv.pop(0))
        else:
            print(f"nieznany przelacznik {argv[0]}")
            return 2
    if not argv:
        print(__doc__)
        return 2

    pub = pathlib.Path(SILNIK) / "public"
    baza = {n: phash(pub / n) for n in sorted(uzyte(SILNIK))
            if (pub / n).exists() and not n.startswith(tuple(pomin) or ("\0",))}
    zle = 0
    with tempfile.TemporaryDirectory() as kat:
        for sciezka in argv:
            nazwa = pathlib.Path(sciezka).name
            plik = pathlib.Path(sciezka)
            if not surowy:
                plik, blad = przez_foto(sciezka, kat)
                if plik is None:
                    print(f"{nazwa:28} ODPADA - foto.py: {' '.join(blad)}")
                    zle += 1
                    continue
            h = phash(plik)
            pary = [(sum(a != b for a, b in zip(h, v)), k)
                    for k, v in baza.items() if k != nazwa]
            if not pary:
                print(f"{nazwa:28} brak czego porownac")
                continue
            d, kto = min(pary)
            stan = "ODPADA" if d <= PROG else ("obejrzyj" if d <= 9 else "ok")
            print(f"{nazwa:28} najblizej {d:2d} do {kto:14} {stan}")
            zle += d <= PROG
    print(f"\nporownane z {len(baza)} zdjeciami ze specyfikacji"
          f"{'' if surowy else ' (po foto.py)'}; odpada: {zle}")
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
