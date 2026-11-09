#!/usr/bin/env python3
"""Liczy dlugosc skryptu rolki PRZED nagraniem.

Lektor czyta ok. 2,5 slowa na sekunde, a KAZDA liczba to srednio 3 slowa
("42%" = "czterdziesci dwa procent"). Przestrzelilem to juz kilka razy
i kazda poprawka to pelny koszt nagrania, dlatego ten skrypt jest bramka.

Uzycie:
    python3 skrypt.py "tekst rolki..."        # albo: ... < plik.txt
"""
import re, sys

# 09.11: przeliczone na 12 nagraniach silnika 4 (47-51 slow mowionych -> 19,3-22,9 s).
# Mediana wyszla 2,37, a nie 2,5 jak szacowalem przy biurku.
TEMPO = 2.37         # slow na sekunde
CEL_MIN, CEL_MAX = 17.0, 21.0
SLOWA_MIN, SLOWA_MAX = 44, 50   # twardsza bramka niz czas: tyle miescilo sie zawsze

LICZEBNIK = {           # ile slow zajmuje wymowienie liczby
    1: 1, 2: 3, 3: 4, 4: 5,
}


def slowa_liczby(tok):
    """Ile slow zajmie wypowiedzenie tokenu z cyframi."""
    cyfry = re.sub(r"\D", "", tok)
    n = len(cyfry)
    baza = LICZEBNIK.get(n, 5 if n else 1)
    if "%" in tok:
        baza += 1          # "procent"
    # przecinek liczy sie tylko MIEDZY cyframi ("4,65"); przecinek na koncu
    # tokenu to interpunkcja i nie dokłada slow (09.11: "95%," liczone jak "9,5%")
    if re.search(r"\d,\d", tok):
        baza += 2          # "i piec dziesiatych"
    return baza


def policz(tekst):
    tokeny = [t for t in re.split(r"\s+", tekst.strip()) if t]
    razem, rozbicie = 0, []
    for t in tokeny:
        n = slowa_liczby(t) if re.search(r"\d", t) else 1
        razem += n
        if n > 1:
            rozbicie.append((t, n))
    return razem, rozbicie, tokeny


def main():
    tekst = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    razem, rozbicie, tokeny = policz(tekst)
    sek = razem / TEMPO
    print(f"tokenow: {len(tokeny)}   slow mowionych: {razem}   szacowany czas: {sek:.1f} s")
    if rozbicie:
        print("  liczby:", ", ".join(f"{t} = {n} sl." for t, n in rozbicie))
    zdania = [z.strip() for z in re.split(r"(?<=[.!?])\s+", tekst.strip()) if z.strip()]
    print(f"  zdan: {len(zdania)}")
    for i, z in enumerate(zdania, 1):
        n, _, _ = policz(z)
        print(f"    {i}. {n/TEMPO:4.1f} s  {z[:70]}")
    if razem > SLOWA_MAX:
        print(f"\nZA DLUGIE: {razem} slow mowionych, limit {SLOWA_MAX} "
              f"(~{sek:.1f} s) - utnij {razem - SLOWA_MAX}.")
        sys.exit(1)
    if razem < SLOWA_MIN:
        print(f"\nZA KROTKIE: {razem} slow mowionych, minimum {SLOWA_MIN} "
              f"- dolóż tresci, nie pauz.")
        sys.exit(1)
    print(f"\nOK - {razem} slow mowionych, okolo {sek:.1f} s.")


if __name__ == "__main__":
    main()
