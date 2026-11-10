# Dekodowanie przez ffmpeg - biblioteka `av` w tym srodowisku nie wspolpracuje
# z faster-whisper (ten sam blad opisany w narzedzia/wymow.py).
import sys, json, subprocess
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for plik in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", plik, "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.float32).copy()
    seg, _ = m.transcribe(audio, language="pl", word_timestamps=True, beam_size=5)
    slowa = [{"s": w.word.strip(), "od": round(w.start, 3), "do": round(w.end, 3)}
             for s in seg for w in s.words]
    out = plik.replace("audio_", "slowa_").replace(".wav", ".json")
    json.dump(slowa, open(out, "w"), ensure_ascii=False)
    print(out, len(slowa), "slow, koniec", slowa[-1]["do"])
