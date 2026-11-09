#!/usr/bin/env python3
"""Udzial pasma 20-120 Hz w energii dzwieku - dowod, ze w rolce JEST muzyka.

Glos sam z siebie daje ok. 3,5%, rolka z podkladem 9-15%. Wydzielone z
produkuj.sh 09.11: heredoc z Pythonem w srodku petli w bashu potrafi zostac
polkniety przez poprzednie podstawienie polecenia i wtedy bash probuje
wykonac linie kodu Pythona jako polecenie.
"""
import subprocess, sys
import numpy as np

raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "2", "-t", "8", "-i", sys.argv[1],
                      "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                     capture_output=True).stdout
x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
X = np.abs(np.fft.rfft(x)) ** 2
f = np.fft.rfftfreq(len(x), 1 / 8000)
print(round(100 * X[(f >= 20) & (f <= 120)].sum() / X.sum(), 2))
