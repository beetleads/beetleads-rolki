#!/usr/bin/env python3
"""Bramka cytowania: zrodlo w tekscie posta musi byc TYM z rejestru.

09.11 napisalem z pamieci piec cytowan do partii 20-22.11 ("Mukherjee, Smith
i Turri, 2018" zamiast "Cheng i Cryder, 2018" i cztery podobne) i zlapalem to
dopiero przy recznym porownaniu z pula. Cytowanie zmyslone brzmi tak samo
wiarygodnie jak prawdziwe, wiec oko go nie wylapie - musi to robic skrypt.

Zasada: w tekscie nie wymyslamy zrodla. Kopiujemy pole `zrodlo` z wpisu w puli,
bo tam trafilo razem ze sprawdzonym linkiem do pelnego tekstu.

Uzycie: python3 zrodla.py [plik_tekstow.json ...]   (domyslnie wszystkie teksty/)
Kod wyjscia: 1 gdy ktorys tekst ma inne zrodlo niz rejestr albo nie ma linku.
"""
import json, pathlib, sys

KAT = pathlib.Path(__file__).resolve().parent
REPO = KAT.parent


def pula():
    out = {}
    for f in (KAT / "pula").glob("*.json"):
        if "plan" in f.name:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        it = d if isinstance(d, list) else d.get("pozycje", [])
        for x in it:
            if isinstance(x, dict) and x.get("nr"):
                out[x["nr"]] = x
    return out


def sprawdz(sciezki):
    p, bledy = pula(), []
    for s in sciezki:
        d = json.loads(pathlib.Path(s).read_text(encoding="utf-8"))
        for kod, t in d.items():
            if not isinstance(t, dict) or "zrodlo" not in t:
                continue            # gotowe-*.json ma zrodlo wtopione w tekst
            wpis = p.get(kod)
            if wpis is None:
                bledy.append((s, kod, "kodu nie ma w puli"))
                continue
            if t["zrodlo"] != wpis["zrodlo"]:
                bledy.append((s, kod,
                              f"tekst: {t['zrodlo']!r}, rejestr: {wpis['zrodlo']!r}"))
            if not wpis.get("link"):
                bledy.append((s, kod, "brak linku do pelnego tekstu w puli"))
    return bledy


if __name__ == "__main__":
    pliki = sys.argv[1:] or sorted(
        str(f) for f in (REPO / "teksty").glob("listopad-*.json"))
    b = sprawdz(pliki)
    for s, kod, co in b:
        print(f"BLAD {pathlib.Path(s).name:22} {kod:5} {co}")
    print(f"\nsprawdzonych plikow: {len(pliki)}, bledow: {len(b)}")
    sys.exit(1 if b else 0)
