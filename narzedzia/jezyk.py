#!/usr/bin/env python3
"""Bramka jezykowa Beetleads (skill `audyt`, sekcja 2) dla silnika 4.

Mechaniczna, bo plynne zdanie przechodzi przez kazda kontrole "na ucho".
Sprawdza teksty z ekranu (dane/n/*.json) i opisy do Metricoola.

Uzycie:
    python3 jezyk.py teksty/listopad-11-13.json dane/n/D1.json ...
"""
import json, re, sys, pathlib

OGONKI = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
ANGLICYZMY = ["second-hand", "sale", "must have", "insight", "brand", "target",
              "deal", "premium", "online shop", "user", "userzy", "lidy", "lidów",
              "lid ", "feedback", "content", "performance", "ROI", "call to action"]
# Slowa, ktore BEZ ogonkow nie istnieja w polszczyznie. Skill `audyt` 2.3:
# kontrola ogonkow NIE ZGADUJE - wersje, ktore same w sobie sa poprawnym wyrazem
# ("swoje", "piec", "czesc", "swoja"), na te liste nie wchodza, bo pierwsza
# wersja takiej kontroli podpowiadala "stó" i "pąragon" i poszla do kosza.
RDZEN = ["wiecej", "niz", "opor", "zrodlo", "sprzedaz", "zakupow", "wiekszy",
         "ktory", "ktora", "ktore", "jesli", "wrecz", "goscie", "swoj",
         "dziewiec", "dziesiec", "polowe", "prosze", "zapamietaj", "wlasciciel",
         "miesiecznie", "najwyzsza", "ponizej", "powyzej"]

def bledy(nazwa, tekst, maks_zdanie=28):
    out = []
    # Hasztagi pisze sie bez ogonkow z zalozenia (#sprzedaz, #zakupow),
    # wiec nie ida do kontroli polskich znakow ani do liczenia zdan.
    tekst = re.sub(r"#\w+", " ", tekst)
    if "—" in tekst or "–" in tekst:
        out.append(("BLAD", nazwa, "dlugi myslnik - ma byc zwykly '-'"))
    for a in ANGLICYZMY:
        if re.search(rf"(?<!\w){re.escape(a)}(?!\w)", tekst, flags=re.I):
            out.append(("uwaga", nazwa, f"anglicyzm albo zla pisownia: {a!r}"))
    if re.search(r"(?<!\w)lid(y|ow|ów|a|em)?(?!\w)", tekst, flags=re.I):
        out.append(("BLAD", nazwa, "pisownia: ma byc 'leady', nie 'lidy'"))
    for w in RDZEN:
        if re.search(rf"(?<!\w){w}(?!\w)", tekst, flags=re.I):
            out.append(("BLAD", nazwa, f"brak polskich znakow: {w!r}"))
    if re.search(r"\b(porownujemy|widzimy|pokazujemy|sprawdzamy|robimy|mamy)\b", tekst, flags=re.I):
        out.append(("uwaga", nazwa, "1. osoba liczby mnogiej w opisie"))
    if re.search(r"\bo\s+procent\b", tekst, flags=re.I):
        out.append(("BLAD", nazwa, "'o procent' bez liczebnika"))
    if re.search(r"\b(dekad[eę]|tydzie[nń]|miesi[ąa]c)\s+(paragon|faktur|zdj[eę][cć])", tekst, flags=re.I):
        out.append(("BLAD", nazwa, "czas policzony rzeczami"))
    for z in re.split(r"(?<=[.!?])\s+", tekst):
        n = len(z.split())
        if n > maks_zdanie:
            out.append(("uwaga", nazwa, f"zdanie na {n} slow: {z[:60]}..."))
    return out

def zbierz(sciezka):
    d = json.loads(pathlib.Path(sciezka).read_text(encoding="utf-8"))
    pary = []
    if isinstance(d, list):          # transkrypcja (*_slowa.json) - nie tekst do kontroli
        return pary
    if "okladka" in d:                       # specyfikacja rolki: teksty z EKRANU
        k = pathlib.Path(sciezka).stem
        o = d["okladka"]; pary.append((f"{k}/okladka", f'{o["l1"]} {o["l2"]}'))
        dm = d["domkniecie"]
        pary.append((f"{k}/domkniecie", " ".join(
            str(dm.get(x, "")) for x in ("naglowek", "linia1", "linia2"))))
        for i, e in enumerate(d.get("elementy", [])):
            t = " ".join(str(e.get(x, "")) for x in
                         ("tekst", "naglowek", "linia1", "linia2", "podpis"))
            if t.strip():
                pary.append((f"{k}/element{i+1}", t))
    else:                                     # teksty do Metricoola
        for kod, v in d.items():
            # Plik zrodlowy ma hook/badanie/mechanizm/rada, gotowy ma ig/fb.
            # Brakujace pola pomijamy, zeby bramka dzialala na obu plikach.
            for pole in ("tytul", "hook", "badanie", "mechanizm", "rada",
                         "pytanie", "ig", "fb"):
                if v.get(pole):
                    pary.append((f"{kod}/{pole}", v[pole]))
    return pary

if __name__ == "__main__":
    wszystkie = []
    for s in sys.argv[1:]:
        for nazwa, tekst in zbierz(s):
            wszystkie += bledy(nazwa, tekst, 28 if "/" in nazwa and
                               nazwa.split("/")[1] in ("badanie", "mechanizm", "rada") else 18)
    for p, n, o in sorted(wszystkie, key=lambda x: x[0] != "BLAD"):
        print(f"{p:7} {n:22} {o}")
    ile = sum(1 for p, _, _ in wszystkie if p == "BLAD")
    print(f"\nbledow: {ile}, uwag: {len(wszystkie) - ile}")
    sys.exit(1 if ile else 0)
