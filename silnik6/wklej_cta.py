"""Podmiana ostatniego zdania (CTA) w nagraniu lektora na nowe ujecie, bez nagrywania calej rolki od nowa.
Uzycie: python3 wklej_cta.py kod  -> glos_<kod>w.wav/json"""
import json, sys, wave, numpy as np
k = sys.argv[1]
def wczytaj(p):
    with wave.open(p) as f:
        return f.getparams(), np.frombuffer(f.readframes(f.getnframes()), np.int16).reshape(-1, f.getnchannels())
par, x = wczytaj(f"glos_{k}.wav")
_, c = wczytaj("glos_cta.wav")
sr = par.framerate
slowa = json.load(open(f"glos_{k}.json"))
i = max(j for j, w in enumerate(slowa) if w["s"].lower().startswith("zaobserwuj"))
t0 = max(0.0, slowa[i]["od"] - 0.04)
n0 = int(t0 * sr)
# krotkie wyciszenie konca przed cieciem (10 ms), zeby nie bylo trzasku
cut = x[:n0].astype(np.float32)
f = int(0.01 * sr)
cut[-f:] *= np.linspace(1, 0, f)[:, None]
cc = c.astype(np.float32) * 10 ** (-1.0 / 20)
y = np.concatenate([cut, cc]).clip(-32768, 32767).astype(np.int16)
with wave.open(f"glos_{k}w.wav", "w") as o:
    o.setparams(par); o.writeframes(y.tobytes())
cta = json.load(open("glos_cta.json"))
nowe = slowa[:i] + [{"s": w["s"], "od": round(w["od"] + t0 + 0.04, 2), "do": round(w["do"] + t0 + 0.04, 2)} for w in cta]
json.dump(nowe, open(f"glos_{k}w.json", "w"), ensure_ascii=False)
print(k, "ciecie", round(t0, 2), "s, koniec", nowe[-1]["do"], "|", " ".join(w["s"] for w in nowe[-6:]))
