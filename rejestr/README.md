# Rejestr tematow rolek Beetleads

Po co: zadna rolka nie moze powtorzyc tematu, ktory juz poszedl.
Karencje (skill `rolki-v3`, sekcja 7): **zrodlo 60 dni**, **mechanizm 5 dni** - wspolnie
dla rolek, karuzel, postow i story.

Plik `tematy.json` to jedno zrodlo prawdy. Kazdy wpis:

```
{
  "rolka": "r213",
  "data": "2026-11-09",
  "godz": "09:00",
  "status": "zaplanowana" | "opublikowana" | "wycofana",
  "slug": "dzemy",
  "zrodlo": "Iyengar i Lepper, 2000",
  "mechanizm": "paradoks wyboru",
  "hook": "6 dzemow kontra 24. Ktore stoisko wygralo?"
}
```

Kontrola przed KAZDYM dodaniem rolki do kolejki:
`python3 rejestr/sprawdz.py` - wypisuje kolizje zrodla (60 dni) i mechanizmu (5 dni).
Rolka z kolizja nie wchodzi do Metricoola.
