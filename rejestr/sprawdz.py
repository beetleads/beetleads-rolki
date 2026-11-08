#!/usr/bin/env python3
"""Kontrola powtorzen tematow. Zwraca kod 1, gdy jest kolizja."""
import json, sys, datetime as dt, pathlib

P = pathlib.Path(__file__).with_name("tematy.json")
wpisy = json.loads(P.read_text(encoding="utf-8"))
żyje = [w for w in wpisy if w.get("status") != "wycofana"]
for w in żyje:
    w["_d"] = dt.date.fromisoformat(w["data"])
żyje.sort(key=lambda w: (w["_d"], w.get("godz", "")))

def norm(s): return " ".join((s or "").lower().replace(",", " ").split())

kolizje = []
for i, a in enumerate(żyje):
    for b in żyje[i + 1:]:
        dni = (b["_d"] - a["_d"]).days
        if norm(a.get("zrodlo")) and norm(a["zrodlo"]) == norm(b["zrodlo"]) and dni <= 60:
            kolizje.append((dni, "ZRODLO", a, b))
        elif norm(a.get("mechanizm")) and norm(a["mechanizm"]) == norm(b["mechanizm"]) and dni <= 5:
            kolizje.append((dni, "MECHANIZM", a, b))

if not kolizje:
    print(f"OK - {len(żyje)} rolek, zero kolizji")
    sys.exit(0)
for dni, typ, a, b in sorted(kolizje):
    print(f"KOLIZJA {typ} ({dni} dni): {a['rolka']} {a['data']} \"{a['slug']}\" "
          f"<-> {b['rolka']} {b['data']} \"{b['slug']}\"  [{a.get('zrodlo')}]")
print(f"\nRazem kolizji: {len(kolizje)}")
sys.exit(1)
