# Remiks zaplanowanych rolek (muzyka + wdechy) - postep

Zmiana zlecona 15.11.2026: "lekko podglosnij muzyke i wytnij wdechy".

## Co robi remiks
`narzedzia/remiks_s6f.py <wejscie.mp4> <wyjscie.mp4>` - dziala na GOTOWEJ rolce:
- rozdziela glos i podklad (demucs htdemucs, two-stems),
- do oryginalnego miksu DODAJE wyseparowany podklad (fazowo zgodny), wiec glos zostaje nietkniety,
- wdechy odejmuje punktowo (tylko POZA slowami lektora - czasy slow z whispera, margines 50 ms, plus odrzucanie fragmentow z tonem krtaniowym),
- kalibruje poziom muzyki do basu 10-13% (`narzedzia/bas.py`),
- rolka bez podkladu (muzyka >30 dB pod glosem): doklada `silnik6/podklad_bit.mp3`,
- obraz kopiowany bez rekompresji (`-c:v copy`), czas i okladka bez zmian.
Kontrola: `narzedzia/remiks_kontrola.py <orig> <nowy>` - obraz identyczny, czas, LUFS, TP, tekst lektora.

Wymaga: `pip install --break-system-packages demucs faster-whisper` (w nowej sesji).

## Publikacja
Plik `<data>_<godz>_<temat>_s6f.mp4` do repo, commit, push, potem `updateScheduledPost`
z adresem `raw.githubusercontent.com/beetleads/beetleads-rolki/<sha>/<plik>.mp4`
(adres z numerem commita, bo Metricool cache'uje raw/main).

## Zrobione (rolki przerobione i podmienione w Metricoolu)
- 15.11 16:00 - 30.11 (31 rolek, 62 posty)
- 1-2.12 (4 rolki, 8 postow)

## Do zrobienia
- 3.12.2026 - 20.01.2027 (2 rolki dziennie, 8:00 i 16:00; po 2 posty na rolke: IG+TikTok i FB+YouTube)

## Co wyszlo przy okazji
- Rolki z 13-14.11: podklad realnie 20-29 dB pod lektorem (bas 4-5% zamiast 9-15%) - przyczyna: sidechain
  i loudnorm w `podklad.py` zjadaly poziom ustawiony przez POD_GLOSEM. Poprawione 15.11 (kalibracja do basu).
- Rolki z 30.11: brak podkladu w ogole (bas ~3%) - doklejony bit.
- Rolki z 27-29.11: muzyka 2,5-3,9 dB pod lektorem (za glosno) - podbicia nie bylo, tylko wyciete wdechy.
