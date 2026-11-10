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

## Ruch - pomiar, nie oko (10.11)

W rolce wzorcowej tylko **1% klatek nie ma ruchu** (mediana roznicy klatek 0,21).
Pierwsza wersja silnika 5 miala 72% klatek bez ruchu i dostala "nie ma efektow",
mimo ze komponenty sie zgadzaly. Sam kadr stojacy miedzy cieciami to za malo.

Dlatego:
- tla sa renderowane z zapasem 17% i okno jedzie przez cale ujecie (`okno()`),
  z wygladzeniem koncow, zeby ciecie nie szarpalo;
- kropki w schemacie wedruja, liczby w slupkach licza sie w gore i unosza,
  ramka karty liczby oddycha, zaznaczone ikonki ludzi pulsuja, chip faluje.

**Bramka przed wyslaniem:** klatki bez ruchu < 10%, mediana roznicy klatek 0,2-0,5.
Za duzo tez jest zle - przy mediannie 0,54 kadr jechal za szybko i trzeba bylo
zmniejszyc amplitude okna do 0,42.
