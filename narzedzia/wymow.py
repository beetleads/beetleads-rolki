#!/usr/bin/env python3
"""Czasy slow z nagrania - lokalnie, bez kredytow.

Zastepuje transkrypcje w ElevenLabs (ok. 114 kredytow na rolke).
Zasada ze skilla zostaje ta sama: czasy slow ZAWSZE z nagrania, nigdy z oszacowania.

Uzycie: python3 wymow.py public/gC1.mp3 dane/n/C1_slowa.json
"""
import json, re, subprocess, sys, pathlib
import numpy as np

def unidecode(t):
    tab = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
    return t.lower().translate(tab)

from faster_whisper import WhisperModel

MODEL = None
def model():
    global MODEL
    if MODEL is None:
        MODEL = WhisperModel("medium", device="cpu", compute_type="int8")
    return MODEL

def pcm(plik):
    """Dekodowanie przez ffmpeg - biblioteka `av` w tym srodowisku nie wspolpracuje
    z faster-whisper, a model i tak przyjmuje gotowa tablice probek 16 kHz."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(plik),
                          "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def slowa(plik):
    seg, _ = model().transcribe(pcm(plik), language="pl", word_timestamps=True,
                                vad_filter=False, beam_size=5)
    out = []
    for s in seg:
        for w in (s.words or []):
            t = w.word.strip()
            if not t:
                continue
            # whisper czasem oddziela znak procentu ("46 %") - napis musi byc jednym slowem
            if t in ("%", "%.", "%,") and out:
                out[-1]["s"] += t
                out[-1]["do"] = round(w.end, 3)
                continue
            # 09.11: to samo robi z przecinkiem dziesietnym - "5 ,2," i "4 ,6."
            # Napis pokazywalby "5", a chwile pozniej ",2," - liczba rozsypana na
            # dwie karty. Lektor mowi jedna liczbe, wiec i napis ma byc jeden.
            if re.match(r"^[,.]\d", t) and out:
                out[-1]["s"] += t
                out[-1]["do"] = round(w.end, 3)
                continue
            out.append({"s": t, "od": round(w.start, 3), "do": round(w.end, 3)})
    # "Zapamietaj" konczy zdanie - buduj.py dzieli zdania po kropce, a od tego
    # zalezy moment wejscia karty domkniecia (08.11: whisper slyszy tu przecinek)
    for i, w in enumerate(out):
        if re.match(r"^zapamietaj[,:;.]?$", unidecode(w["s"])):
            w["s"] = w["s"].rstrip(",:;.") + "."
            if i + 1 < len(out):      # napisy ida bez zmiany wielkosci liter
                n = out[i + 1]["s"]
                out[i + 1]["s"] = n[:1].upper() + n[1:]
    return out

if __name__ == "__main__":
    wej, wyj = sys.argv[1], sys.argv[2]
    w = slowa(wej)
    pathlib.Path(wyj).write_text(json.dumps(w, ensure_ascii=False), encoding="utf-8")
    print(f"{wyj}: {len(w)} slow, koniec {w[-1]['do']}s")
