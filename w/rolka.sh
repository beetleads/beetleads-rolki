#!/bin/bash
# rolka.sh <katalog> [url_glosu]  -> pobiera głos (opcjonalnie), build, render, qa
set -e; W=/home/claude/beetleads-rolki/w; D=$1
[ -n "$2" ] && curl -sS -o $D/voice.mp3 "$2"
python3 $W/build.py $D 2>&1 | grep '^{'
python3 $W/render.py $D > /dev/null
python3 $W/qa.py $D 2>&1 | grep '^{'
