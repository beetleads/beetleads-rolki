#!/bin/bash
# Partia rolek: buduj -> renderuj -> muzyka -> kontrola. Log na stdout.
cd /home/claude/silnik4
for K in "$@"; do
  echo "=== $K ==="
  python3 buduj.py dane/n/$K.json dane/n/${K}_slowa.json -o dane/aktualna.json || { echo "$K: BLAD buduj"; continue; }
  bash /home/claude/produkuj.sh $K /home/claude/beetleads-rolki/rolki/n_$K.mp4 || echo "$K: BLAD produkuj"
done
echo "=== KONIEC PARTII ==="
