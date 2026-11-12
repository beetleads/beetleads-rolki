# Silnik 6 (12.11)

Rolka = animowane wyjasnienie. Pytanie od ludzi -> mechanizm pokazany obrazem jak
dla pieciolatka -> jeden dowod -> CTA "Zaobserwuj profil po wiecej ciekawostek".

Kolejnosc:
1. Lektor: ElevenLabs, glos ROLKI, eleven_v4, podawka [confident, warm], JEDNO ujecie.
2. `python3 przerob_glos.py kod:plik.mp3` -> glos_kod.wav + glos_kod.json (slowa z czasami).
   Poprawic tokeny (liczby cyframi, dwukropki).
3. Napisac `rolka_kod.json`: sceny startuja na slowach lektora (`"od": "Bywa"`).
4. `python3 silnik6.py rolka_kod.json raw_kod.mp4`
5. `python3 finisz.py raw_kod.mp4 raw_kod.spec.json gotowa_kod.mp4`
6. Bramki: waliduj.py, sprawdz_start.py + obejrzec klatki kazdej sceny.

Nowe sceny dopisuje sie jako funkcje `scena_*` i rejestruje w `SCENY`.
Kazdy temat ma dostac WLASNA animacje mechanizmu, nie szablon.
