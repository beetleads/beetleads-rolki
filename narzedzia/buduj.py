#!/usr/bin/env python3
"""Buduje dane/aktualna.json dla rolki Beetleads z silnika 4.

Wejscie: plik JSON ze specyfikacja tematu + transkrypcja nagrania (czasy slow).
Wyjscie: dane/aktualna.json gotowe do `npx remotion render Rolka`.

Zasady, ktore ten skrypt pilnuje za mnie (08.11):
  - NOWE UJECIE co ok. 2 s. Przy ujeciach po 4-5 s rolka czuje sie statycznie.
  - Ujecie STOI (tryb `kadry` w Zdjecie.tsx), wiec dlugosc ujecia to jedyne,
    co daje ruch - nie wolno jej rozciagac.
  - Ostatnie ujecie pelnej dlugosci, zero blysku na koncu.
  - Kazde zdanie niesie element, zeby kadr nigdy nie byl sam.
  - Czasy slow ZAWSZE z transkrypcji nagrania, nigdy z oszacowania.

Uzycie:
    python3 buduj.py temat.json slowa.json [-o dane/aktualna.json]

temat.json:
{
  "glos": "g301.mp3",
  "akcent": "#FFD84D",
  "okladka": {"l1": "...", "l2": "...", "akcent": "77%", "emoji": "😳"},
  "foty": ["a.jpg", "b.jpg", "c.jpg"],
  "fokusy": [[50,45],[50,50],[50,55]],      # opcjonalne, domyslnie [50,50]
  "domkniecie": {"naglowek": "ZROB TO U SIEBIE", "linia1": "...", "linia2": "..."},
  "elementy": [                              # jeden na zdanie, po kolei
    {"typ": "pigulka", "tekst": "EKSPERYMENT W SKLEPIE", "y": 270},
    {"typ": "karta", "naglowek": "...", "linia1": "...", "linia2": "...", "y": 1205},
    {"typ": "slupki", "a": {"etykieta":"A","wartosc":30}, "b": {"etykieta":"B","wartosc":3}, "y": 300},
    {"typ": "ludzie", "ile": 44, "podpis": "TYLKO 6 PRZYZNALO", "y": 330}
  ]
}

slowa.json: lista {"text"|"s", "start"|"od", "end"|"do"} z transkrypcji.
"""
import argparse, json, pathlib, re, sys

UJECIE_MIN = 1.6          # krocej niz tyle i ciecia sa nerwowe
UJECIE_MAX = 2.4          # dluzej i ujecie zaczyna stac
DOMKNIECIE_PRZED = 0.25   # karta wniosku wchodzi tuz przed ostatnim zdaniem


def wczytaj_slowa(p):
    sur = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    if isinstance(sur, dict):
        sur = sur.get("words") or sur.get("slowa") or []
    out = []
    for w in sur:
        if w.get("type") and w["type"] != "word":
            continue
        s = w.get("s") or w.get("text") or ""
        if not s.strip():
            continue
        out.append({"s": s, "od": float(w.get("od", w.get("start"))),
                    "do": float(w.get("do", w.get("end")))})
    if not out:
        sys.exit("brak slow w transkrypcji")
    return out


def zdania(slowa):
    """Dzieli slowa na zdania po koncowej interpunkcji."""
    grupy, biez = [], []
    for w in slowa:
        biez.append(w)
        if re.search(r"[.!?]$", w["s"]):
            grupy.append(biez); biez = []
    if biez:
        grupy.append(biez)
    return grupy


def ujecia(dlugosc, n_fot):
    """Granice ujec: rowne, dlugosc w przedziale UJECIE_MIN..UJECIE_MAX,
    ostatnie ujecie zawsze pelnej dlugosci."""
    n = max(1, round(dlugosc / 2.0))
    while dlugosc / n > UJECIE_MAX:
        n += 1
    while n > 1 and dlugosc / n < UJECIE_MIN:
        n -= 1
    krok = dlugosc / n
    return [(round(i * krok, 3), round((i + 1) * krok, 3)) for i in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("temat")
    ap.add_argument("slowa")
    ap.add_argument("-o", "--out", default="dane/aktualna.json")
    a = ap.parse_args()

    t = json.loads(pathlib.Path(a.temat).read_text(encoding="utf-8"))
    slowa = wczytaj_slowa(a.slowa)
    dlugosc = round(slowa[-1]["do"] + 0.25, 2)

    foty = t["foty"]
    fokusy = t.get("fokusy") or [[50, 50]] * len(foty)
    granice = ujecia(dlugosc, len(foty))
    sceny = [{"foto": foty[i % len(foty)],
              "fokus": fokusy[i % len(fokusy)],
              "od": od, "do": do} for i, (od, do) in enumerate(granice)]

    zd = zdania(slowa)
    el_spec = t.get("elementy", [])
    elementy = []
    nast = 0
    for e in el_spec:
        # "zdanie": n wiaze element z konkretnym zdaniem (1-based); bez tego - po kolei
        if "zdanie" in e:
            i = e["zdanie"] - 1
        else:
            i = nast; nast += 1
        if i >= len(zd) or i < 0:
            print(f"  UWAGA: element {e.get('typ')} wskazuje zdanie {i+1}, a zdan jest {len(zd)} - pominiety")
            continue
        do_zd = e.pop("doZdania", None)
        j = (do_zd - 1) if do_zd else i
        j = min(j, len(zd) - 1)
        od = round(zd[i][0]["od"] - 0.08, 3)
        do = round(zd[j][-1]["do"] + 0.12, 3)
        e = {k: v for k, v in e.items() if k != "zdanie"}
        # 09.11: "STARA PO LEWEJ" obok "PO PRAWEJ" nachodzily na siebie nad
        # slupkami - etykieta jest centrowana nad slupkiem 152 px, wiec dluga
        # wchodzi na sasiednia. Bramka, zeby nie wylapywac tego dopiero okiem.
        if e.get("typ") == "slupki":
            for strona in ("a", "b"):
                et = e.get(strona, {}).get("etykieta", "")
                if len(et) > 13:
                    print(f"  UWAGA: etykieta slupka {et!r} ma {len(et)} znakow "
                          f"- powyzej 13 nachodzi na sasiednia")
        elementy.append({**e, "od": max(0.0, od), "do": min(dlugosc, do)})

    # domkniecie wchodzi przed ostatnim zdaniem i zostaje do konca
    od_dom = round(zd[-1][0]["od"] - DOMKNIECIE_PRZED, 2) if zd else round(dlugosc - 3, 2)

    # Impuls to obwodka w miejscu karty domkniecia. Wiazany ze zdaniem wchodzil
    # pol sekundy PRZED karta i przez ten czas na ekranie stal pusty prostokat -
    # wyglada jak blad, nie jak efekt (09.11, koncowka C6). Puszczamy go razem
    # z karta, zeby byl jej wejsciem, a nie osobnym ksztaltem.
    for e in elementy:
        if e.get("typ") == "impuls" and (e.get("y") or 1180) >= 1000:
            przesun = max(0.0, od_dom - 0.12) - e["od"]
            e["od"] = round(e["od"] + przesun, 3)
            e["do"] = round(min(dlugosc, e["do"] + przesun), 3)
    dane = {
        "glos": t["glos"],
        "dlugosc": dlugosc,
        "akcent": t.get("akcent", "#FFD84D"),
        "slowa": slowa,
        "sceny": sceny,
        "elementy": elementy,
        "okladka": t["okladka"],
        "domkniecie": {"od": max(0.5, od_dom), **t["domkniecie"]},
    }
    pathlib.Path(a.out).write_text(
        json.dumps(dane, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{a.out}: dlugosc {dlugosc}s, ujec {len(sceny)} "
          f"(po {round(dlugosc/len(sceny),2)}s), zdan {len(zd)}, "
          f"elementow {len(elementy)}, domkniecie od {dane['domkniecie']['od']}s")
    if len(el_spec) > len(zd):
        print(f"  UWAGA: podano {len(el_spec)} elementow, a zdan jest {len(zd)} "
              f"- nadmiarowe pominieto")


if __name__ == "__main__":
    main()
