#!/usr/bin/env python3
"""Kontrola powtorzen tematow rolek Beetleads.

Karencje (skill rolki-v3, sekcja 7):
  - ZRODLO: 60 dni. Kolizja takze wtedy, gdy rok jest inny, a autorzy ci sami -
    08.11 wyszlo, ze North/Hargreaves/McKendrick 1997 i 1999 to dla widza
    dokladnie ta sama rolka o muzyce w sklepie.
  - MECHANIZM: 5 dni to za malo. 03.11 poszly pieczatki na karcie myjni
    (Nunes i Dreze), a na 10.11 stala karta kawiarni (Kivetz) - inni autorzy,
    ten sam gradient celu, 7 dni odstepu i widz widzi powtorke.
    Dlatego: do 5 dni BLAD, do 30 dni OSTRZEZENIE do recznej decyzji.

HISTORIA kontra PLAN (09.11): kolizja miedzy dwiema rolkami, ktore JUZ
poszly w swiat, jest zapisem bledu, a nie czyms do naprawienia - nie da sie
cofnac publikacji. Bramka ma zatrzymywac to, co jeszcze mozna zmienic, wiec
blokuje tylko wtedy, gdy w kolizji bierze udzial rolka nieopublikowana.
Stare kolizje nadal wypisuje, pod naglowkiem HISTORIA.

Kod wyjscia: 1 gdy jest BLAD do naprawienia, 0 gdy czysto, same ostrzezenia
albo sama historia.
"""
import json, re, sys, datetime as dt, pathlib

ZRODLO_DNI = 60
MECH_BLAD_DNI = 5
MECH_OSTRZ_DNI = 30

P = pathlib.Path(__file__).with_name("tematy.json")
wpisy = json.loads(P.read_text(encoding="utf-8"))
zywe = [w for w in wpisy if w.get("status") != "wycofana"]
for w in zywe:
    w["_d"] = dt.date.fromisoformat(w["data"])
zywe.sort(key=lambda w: (w["_d"], w.get("godz", "")))


def norm(s):
    return " ".join((s or "").lower().replace(",", " ").split())


def autorzy(zrodlo):
    """Zbior nazwisk ze zrodla, bez roku i bez 'i in.'."""
    s = norm(zrodlo)
    if not s or s == "-":
        return frozenset()
    s = re.sub(r"\b(19|20)\d{2}\b", " ", s)
    s = s.replace(" i in.", " ").replace(" i inni", " ").replace(" i ", " ")
    czesci = [c.strip(" .") for c in s.split()]
    return frozenset(c for c in czesci if len(c) > 2)


def opis(w):
    return f"{w.get('rolka','-')} {w['data']} {w.get('godz','')} \"{w['slug']}\""


bledy, ostrzezenia = [], []
for i, a in enumerate(zywe):
    for b in zywe[i + 1:]:
        dni = (b["_d"] - a["_d"]).days
        za, zb = autorzy(a.get("zrodlo")), autorzy(b.get("zrodlo"))
        if za and zb and za == zb and dni <= ZRODLO_DNI:
            bledy.append((dni, "ZRODLO", a, b, a.get("zrodlo")))
            continue
        ma, mb = norm(a.get("mechanizm")), norm(b.get("mechanizm"))
        if ma and mb and ma == mb and ma != "-":
            if dni <= MECH_BLAD_DNI:
                bledy.append((dni, "MECHANIZM", a, b, ma))
            elif dni <= MECH_OSTRZ_DNI:
                ostrzezenia.append((dni, "MECHANIZM", a, b, ma))

def doNaprawy(a, b):
    return a.get("status") != "opublikowana" or b.get("status") != "opublikowana"

czynne = [k for k in bledy if doNaprawy(k[2], k[3])]
historia = [k for k in bledy if not doNaprawy(k[2], k[3])]
for dni, typ, a, b, co in sorted(czynne, key=lambda k: k[0]):
    print(f"BLAD {typ} ({dni} dni): {opis(a)} <-> {opis(b)}  [{co}]")
for dni, typ, a, b, co in sorted(historia, key=lambda k: k[0]):
    print(f"HISTORIA {typ} ({dni} dni): {opis(a)} <-> {opis(b)}  [{co}]")
for dni, typ, a, b, co in sorted(ostrzezenia, key=lambda k: k[0]):
    print(f"OSTRZEZENIE {typ} ({dni} dni): {opis(a)} <-> {opis(b)}  [{co}]")

print(f"\n{len(zywe)} rolek, bledow do naprawy: {len(czynne)}, "
      f"kolizji w historii: {len(historia)}, ostrzezen: {len(ostrzezenia)}")
sys.exit(1 if czynne else 0)
