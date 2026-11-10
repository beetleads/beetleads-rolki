# Silnik 5 - rysowane sceny, bez przegladarki

Powstal 10.11, bo silnik 4 (Remotion) nie byl w repo i jego jezyk wizualny
zgubil polowe komponentow: przez wiekszosc rolki na ekranie zostawalo samo
zdjecie z napisem. Ten silnik jest w repo w calosci - zaden styl juz nie ucieka.

- `render.py spec.json wyjscie.mp4` - render 1080x1920, 30 kl./s, audio doklejane z `spec["audio"]`
- `fonty/` - Anton (scalone subsety latin + latin-ext, inaczej polskie znaki wychodza kwadratami) i Inter
- `przyklad_spec.json` - kompletny przyklad (rolka "ryczalt czy licznik")

Komponenty: chip, slupki A/B, siatka ludzi, schemat mechanizmu, karta liczby
("POLICZONE W BADANIU"), karta domkniecia ("ZROB TO U SIEBIE"), pigulka
ZAPAMIETAJ, napisy karaoke, @beetleads na kazdej klatce.

Zasady: ujecie STOI (zmiana tylko na cieciu, nowe ujecie co ok. 1,6-2,2 s),
kazde zdanie niesie element, dol sceny nigdy pusty, czasy slow ZAWSZE
z transkrypcji nagrania, napisy lamane po zdaniach i pauzach.
