#!/usr/bin/env python3
"""Czy kandydat na zdjecie nie powtarza kadru - SPRAWDZANE PRZED wejsciem do public/.

09.11: bramka zdjecia.py lapala kolizje dopiero po wlozeniu pliku do public/ i po
pelnym ogledzie w rozdzielczosci. Jeden kandydat (nT2u--BJWlE) przeszedl foto.py
i caly ogled, a potem wylecial na odleglosci 6 do trzech plikow naraz - stracony
cykl. Ten skrypt liczy hash kandydata z pliku surowego albo przetworzonego i podaje
najmniejsza odleglosc do calej biblioteki wpisanej do specyfikacji.

Uzycie:
    python3 kandydat.py /sciezka/do/kandydata.jpg [kolejny.jpg ...]
    python3 kandydat.py --pomin P5_ P11_ kandydat.jpg      # pomin wlasne stare pliki

Odleglosc <= 6 = dla oka ten sam kadr, nie bierz. 7-9 = obejrzyj pare obok pary.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from zdjecia import phash, uzyte

PROG = 6
SILNIK = "/home/claude/silnik4"


def main(argv):
    pomin = []
    if argv and argv[0] == "--pomin":
        argv = argv[1:]
        while argv and not argv[0].lower().endswith((".jpg", ".jpeg", ".png")):
            pomin.append(argv.pop(0))
    if not argv:
        print(__doc__)
        return 2
    pub = pathlib.Path(SILNIK) / "public"
    baza = {n: phash(pub / n) for n in sorted(uzyte(SILNIK))
            if (pub / n).exists() and not n.startswith(tuple(pomin) or ("\0",))}
    zle = 0
    for sciezka in argv:
        nazwa = pathlib.Path(sciezka).name
        h = phash(pathlib.Path(sciezka))
        # plik juz wpisany do specyfikacji porownywalby sie sam ze soba
        pary = [(sum(a != b for a, b in zip(h, v)), k) for k, v in baza.items() if k != nazwa]
        if not pary:
            print(f"{nazwa:28} brak czego porownac")
            continue
        d, kto = min(pary)
        stan = "ODPADA" if d <= PROG else ("obejrzyj" if d <= 9 else "ok")
        print(f"{nazwa:28} najblizej {d:2d} do {kto:14} {stan}")
        zle += d <= PROG
    print(f"\nporownane z {len(baza)} zdjeciami ze specyfikacji; odpada: {zle}")
    return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
