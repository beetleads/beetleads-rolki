#!/usr/bin/env python3
"""Sklada spec rolki z czasow slow + opisu tematu, wg wzorca z 10.11.

Zasady, ktore ten skrypt pilnuje za mnie:
  - trzy pasy zajete przez caly czas (gora: ilustracja, srodek: napisy, dol: karta)
  - hook ma wlasna ilustracje od 0,5 s - to najcenniejsze sekundy
  - ujecie 1,7-2,1 s, tla naprzemiennie zdjecie / desen
  - koncowka: tabliczka "WNIOSEK MARKETINGOWY", ptaszek i krzyzyk, follow z klikiem
"""
import json, pathlib, sys

P = "/home/claude/silnik5/public/"


def zdania(slowa):
    zd, b = [], []
    for x in slowa:
        b.append(x)
        if x["s"].rstrip()[-1:] in ".?!":
            zd.append(b)
            b = []
    if b:
        zd.append(b)
    return [(z[0]["od"], z[-1]["do"]) for z in zd]


def buduj(t):
    slowa = json.load(open(f"/home/claude/silnik5/glos_{t['kod']}.json"))
    zd = zdania(slowa)
    dl = round(slowa[-1]["do"] + 0.35, 2)
    i_pyt = t.get("i_pytanie", len(zd) - 3)      # zdanie "Wiesz dlaczego?"
    i_mech = i_pyt + 1
    i_wniosek = i_mech + 1

    # ujecia co ok. 1,9 s, tla na zmiane: zdjecie, desen, zdjecie...
    ujecia, czas, nr = [], 0.1, 0
    while czas < dl - 0.1:
        do = min(dl, czas + 1.9)
        if nr % 2 == 0:
            plik = t["foty"][(nr // 2) % len(t["foty"])]
            tlo = {"typ": "foto", "plik": P + plik, "kadr": nr}
        else:
            tlo = {"typ": "desen", "ziarno": 11 + nr * 5}
        ujecia.append({"od": round(czas, 2), "do": round(do, 2), "tlo": tlo})
        czas, nr = do, nr + 1

    el = []
    # HOOK: chip + karty + karta na dole
    el.append({"typ": "chip", "tekst": t["chip"], "od": 0.15, "do": round(zd[0][1] + 0.2, 2), "y": 150})
    el.append({"typ": "karty", "karty": t["karty"], "od": 0.5, "do": round(zd[0][1] + 0.2, 2), "y": 330})
    el.append({"typ": "karta_liczby", "naglowek": "Na start", "l1": t["start"][0], "l2": t["start"][1],
               "od": 0.75, "do": round(zd[0][1] + 0.2, 2), "y": 1150})

    # DOWOD: ilustracja u gory przez cala czesc badawcza + dwie karty na dole.
    # Start NIE moze wyprzedzic konca kart hooka - 10.11 bramka kolizji zlapala
    # nachodzenie kart na slupki w 3,4-3,8 s.
    koniec_hooka = zd[0][1] + 0.2
    od_b, do_b = max(zd[1][0] - 0.1, koniec_hooka + 0.05), zd[i_pyt - 1][1] + 0.15
    el.append(dict(t["dowod"], od=round(od_b, 2), do=round(do_b, 2), y=t["dowod"].get("y", 240)))
    pol = round((od_b + do_b) / 2, 2)
    el.append({"typ": "karta_liczby", "naglowek": "Próba badania", "l1": t["proba"][0], "l2": t["proba"][1],
               "od": round(od_b + 0.15, 2), "do": pol, "y": 1150})
    el.append({"typ": "karta_liczby", "naglowek": "Policzone w badaniu", "l1": t["wynik"][0], "l2": t["wynik"][1],
               "od": pol, "do": round(zd[i_pyt][1] + 0.3, 2), "y": 1150})

    # MECHANIZM
    el.append({"typ": "chip", "tekst": "Dlaczego tak jest", "od": round(zd[i_pyt][0], 2),
               "do": round(zd[i_mech][0] - 0.05, 2), "y": 150})
    start_k = round(zd[i_wniosek][0] - 0.2, 2)
    # schemat i karta mechanizmu musza skonczyc sie, ZANIM wejdzie koncowka
    el.append({"typ": "schemat", "etykieta": t["schemat"][1], "podpis": t["schemat"][0],
               "od": round(zd[i_mech][0], 2),
               "do": round(min(zd[i_mech][1] + 0.2, start_k + 0.02), 2), "y": 430})
    el.append({"typ": "karta_liczby", "naglowek": "Dlaczego tak jest", "l1": t["mech"][0], "l2": t["mech"][1],
               "od": round(zd[i_pyt][1] + 0.3, 2),
               "do": round(min(zd[i_mech][1] + 0.25, start_k + 0.02), 2), "y": 1150})

    # KONCOWKA
    el.append({"typ": "tabliczka", "tekst": "Wniosek marketingowy", "od": start_k, "do": round(dl - 0.15, 2), "y": 130})
    el.append({"typ": "tak_nie", "podpis": t["tak_nie"], "od": round(start_k + 0.1, 2),
               "do": round(dl - 2.0, 2), "y": 330})
    el.append({"typ": "follow", "podpis": "po więcej treści marketingowych", "klik": 0.95,
               "od": round(dl - 1.95, 2), "do": round(dl - 0.15, 2), "y": 330})
    el.append({"typ": "domkniecie", "naglowek": "Zrób to u siebie", "l1": t["rada"][0], "l2": t["rada"][1],
               "od": round(start_k + 0.05, 2), "do": round(dl - 0.15, 2), "y": 1180})

    spec = {"audio": f"/home/claude/silnik5/glos_{t['kod']}.wav", "dlugosc": dl,
            "akcent": t.get("akcent", "#FFD84D"), "cyjan": t.get("cyjan", "#35D0E8"),
            "okladka_do": 0.1,
            "okladka": {"l1": t["okladka"][0], "l2": t["okladka"][1], "foto": P + t["foty"][0]},
            "ujecia": ujecia, "elementy": el, "slowa": slowa,
            "klik_dzwiek": round(dl - 1.95 + 0.95, 2)}
    out = f"/home/claude/silnik5/spec_{t['kod']}.json"
    json.dump(spec, open(out, "w"), ensure_ascii=False, indent=1)
    print(out, "dlugosc", dl)
    return out


if __name__ == "__main__":
    for opis in json.load(open(sys.argv[1])):
        buduj(opis)
