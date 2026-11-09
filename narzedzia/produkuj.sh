#!/bin/bash
# Produkcja rolki Beetleads od zera (silnik 4).
#   ./produkuj.sh <kod> <wyjscie.mp4>
# Wymaga: dane/aktualna.json juz zbudowane przez buduj.py
#
# Co robi i dlaczego:
#  - renderuje kompozycje Rolka (ujecia STOJA, zmiana tylko na cieciu)
#  - podklada PRAWDZIWA muzyke z public/podklad.wav i dobiera glosnosc tak,
#    zeby bas 20-120 Hz wypadl w przedziale wzorcowym 9-15%; bez tego rolka
#    wychodzi bez muzyki, co zdarzylo sie przy r216 i r217
#  - 09.11: dobor glosnosci i pomiar LUFS ida na SAMYM DZWIEKU (wav), a obraz
#    koduje sie RAZ. Wczesniej kazda proba przekodowywala caly film - trzy
#    proby to byly trzy kodowania h264 na nic
#  - limiter bez makeup gain (level=disabled); sufit 0,80, bo AAC przestrzeliwuje
#    przy kodowaniu (C6 wyszlo -1,1 dB przy sufiveie 0,84)
#  - kontroluje: liczba klatek = dlugosc x 30, szczyt <= -1,3 dB, -14 LUFS +/- 1
set -e
KOD=$1; OUT=$2
mkdir -p "$(dirname "$OUT")"
S=/tmp/claude-0/-home-claude/20636ca7-5aeb-5796-9ee4-a60caa8f4d9f/scratchpad
cd /home/claude/silnik4
export REMOTION_CHROME_EXECUTABLE=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome

npx remotion render Rolka "$S/sur_${KOD}.mkv" --codec=h264 --log=error >/dev/null
DL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$S/sur_${KOD}.mkv")
KONIEC=$(python3 -c "print(round($DL-0.8,2))")

# Filtr miksu: $1 = glosnosc podkladu, $2 = korekta glosnosci w dB.
# Kolejnosc limiterow jest wazna: najpierw limiter miksu (0,84), POTEM korekta
# do -14 LUFS, potem limiter koncowy. Gdyby korekta szla przed pierwszym
# limiterem, dodanie +3,7 dB (tyle potrzebowalo D1) zostaloby sciete i rolka
# wyszlaby cichsza, niz pokazuje pomiar.
mix_filtr() {
  echo "[1:a]atrim=0:${DL},asetpts=N/SR/TB,volume=$1,afade=t=in:st=0:d=0.6,afade=t=out:st=${KONIEC}:d=0.8[m];\
[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=disabled,\
volume=$2dB,alimiter=limit=${SUFIT:-0.80}:level=disabled[a]"
}

# 1. dobor glosnosci podkladu - tylko dzwiek, bez dotykania obrazu
G=1.2
for PROBA in 1 2 3; do
  ffmpeg -v error -i "$S/sur_${KOD}.mkv" -i public/podklad.wav \
    -filter_complex "$(mix_filtr $G 0)" -map "[a]" -c:a pcm_s16le "$S/pr_${KOD}.wav" -y
  BAS=$(python3 -I bas.py "$S/pr_${KOD}.wav")
  echo "  proba $PROBA: podklad x$G -> bas ${BAS}%"
  OK=$(python3 -c "print(1 if 9 <= $BAS <= 15 else 0)")
  [ "$OK" = "1" ] && break
  G=$(python3 -c "print(round($G * (12.0/max($BAS,1.0))**0.5, 2))")
done

# 2. korekta do -14 LUFS liczona na tym samym dzwieku
LM=$(ffmpeg -i "$S/pr_${KOD}.wav" -af ebur128=framelog=quiet -f null - 2>&1 | grep -oE "I: +[-0-9.]+ LUFS" | tail -1 | grep -oE "[-0-9.]+")
DELTA=$(python3 -c "print(round(-14.0 - ($LM), 2))")

# 3. jedno kodowanie obrazu; przy przestrzelonym szczycie schodzi sam sufit limitera
SUFIT=0.80
for PROBA_P in 1 2 3; do
  ffmpeg -v error -i "$S/sur_${KOD}.mkv" -i public/podklad.wav \
    -filter_complex "$(mix_filtr $G $DELTA)" -map 0:v -map "[a]" \
    -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 30 \
    -c:a aac -b:a 192k -ar 44100 -movflags +faststart "$OUT" -y
  P=$(ffmpeg -i "$OUT" -af volumedetect -f null - 2>&1 | grep -oE "max_volume: [-0-9.]+" | cut -d' ' -f2)
  python3 -c "import sys; sys.exit(0 if $P <= -1.3 else 1)" && break
  SUFIT=$(python3 -c "print(round($SUFIT * 0.92, 3))")
  echo "  szczyt $P dB za wysoko - obnizam sufit limitera do $SUFIT"
done
echo "  korekta glosnosci: ${LM} -> -14 LUFS (${DELTA} dB), sufit limitera ${SUFIT}"

# kontrola koncowa
N=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0 "$OUT")
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
L=$(ffmpeg -i "$OUT" -af ebur128=framelog=quiet -f null - 2>&1 | grep -oE "I: +[-0-9.]+ LUFS" | tail -1 | grep -oE "[-0-9.]+")
OCZ=$(python3 -c "print(round($D*30))")
echo "$KOD: dl=$D klatki=$N (oczekiwane $OCZ) bas=${BAS}% szczyt=$P LUFS=$L"
[ "$N" = "$OCZ" ] || echo "  BLAD: liczba klatek nie zgadza sie z dlugoscia"
python3 -c "import sys; sys.exit(0 if $P <= -1.3 else 1)" || echo "  BLAD: szczyt za wysoko ($P dB)"
python3 -c "import sys; sys.exit(0 if -15.2 <= $L <= -12.8 else 1)" || echo "  BLAD: glosnosc poza -14 LUFS +/- 1 ($L)"

# okladka do YouTube: pierwsza klatka
ffmpeg -v error -ss 0.03 -i "$OUT" -frames:v 1 "${OUT%.mp4}_yt.jpg" -y
echo "  okladka: ${OUT%.mp4}_yt.jpg"
