#!/bin/bash
# zrob.sh KOD : hybryda -> finisz -> podklad -> walidacja -> arkusz kontrolny
set -eo pipefail
k=$1; H=/home/claude/hf; S=/tmp/claude-0/-home-claude/2dbe75ca-4db3-575f-9da9-3016388c7a29/scratchpad/k
cd /home/claude/silnik6 && python3 hybryda.py hyb_${k}w.json $H/raw_${k}h.mp4 | tail -1
cd /home/claude/silnik5 && python3 finisz.py $H/raw_${k}h.mp4 $H/raw_${k}h.spec.json $H/gotowa_${k}h.mp4 | tail -1
cd /home/claude/silnik6 && python3 podklad.py $H/gotowa_${k}h.mp4 podklad_bit.mp3 $H/${k}e.mp4 | tail -1
python3 /home/claude/silnik5/waliduj.py $H/${k}e.mp4 | tail -1
python3 /home/claude/silnik5/sprawdz_start.py $H/${k}e.mp4 | tail -1
ffmpeg -v error -y -i $H/${k}e.mp4 -vf "fps=1.2,scale=180:-1,tile=13x2" -frames:v 1 $S/${k}e.jpg
