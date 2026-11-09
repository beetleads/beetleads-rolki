# Narzędzia produkcji rolek (silnik 4)

Kolejność pracy nad partią dziewięciu rolek:

| krok | skrypt | po co |
|---|---|---|
| 1. tekst | `skrypt.py "..."` | bramka długości PRZED nagraniem: 44-50 słów mówionych (przeliczone na 12 nagraniach: tempo 2,37 sł./s) |
| 2. język | `jezyk.py teksty.json dane/n/*.json` | polskie znaki, krótki myślnik, "leady" nie "lidy", brak 1. osoby w opisie |
| 3. nagranie | ElevenLabs, głos ROLKI, `generations_count: 1` | szablon tagów: `[confident, giving advice]` fakty, `[intrigued]` pytanie, `[confident, warm]` mechanizm, `[confident]` wniosek |
| 4. ton | `glos.py public/g*.mp3` | pasmo 126-136 Hz. 09.11: bez szablonu tagów ta sama treść schodzi do 117-124 Hz |
| 5. czasy słów | `wymow.py public/gX.mp3 dane/n/X_slowa.json` | lokalnie, bez kredytów; sprawdzone na trzech rolkach wobec ElevenLabs (mediana różnicy 20-40 ms) |
| 6. zdjęcia | `foto.py oryginal.jpg public/X_1.jpg` | kadr 9:16, jasność 45-90. Podłoga liczona NA ORYGINALE - ratowanie gotowego, przyciemnionego pliku rozwala cienie na pasy |
| 7. powtórzenia | `rejestr/zdjecia.py`, `rejestr/sprawdz.py` | to samo zdjęcie pod dwoma tematami; powtórka źródła i mechanizmu |
| 8. montaż | `buduj.py dane/n/X.json dane/n/X_slowa.json` | ujęcia co ok. 2 s, elementy wiązane ze zdaniami |
| 9. render + muzyka | `partia.sh X Y Z` (woła `produkuj.sh`) | render, podkład z doborem głośności do basu 9-15%, -14 LUFS, kontrola klatek i szczytu |

Kontrola końcowa jest w `produkuj.sh`: liczba klatek = długość x 30, szczyt <= -1,3 dB,
głośność -14 LUFS ±1, udział basu 20-120 Hz w przedziale 9-15% (dowód, że muzyka jest).
