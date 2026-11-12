"""Nowy glos -> wav -> audio6 -> whisper -> poprawki tokenow. Argumenty: kod:mp3 ..."""
import json, subprocess, sys, numpy as np
from faster_whisper import WhisperModel
S = "/home/claude/silnik5"
M = WhisperModel("medium", device="cpu", compute_type="int8")

def wav16(p):
    raw = subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","16000","-f","f32le","-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def scal(d,i,j,s):
    d[i] = {"s": s, "od": d[i]["od"], "do": d[j]["do"]}; del d[i+1:j+1]

for arg in sys.argv[1:]:
    kod, mp3 = arg.split(":")
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"{S}/{mp3}","-ac","2","-ar","48000",
                    "-c:a","pcm_s16le",f"{S}/sur_{kod}.wav"], check=True)
    subprocess.run([sys.executable,"-I","audio6.py",f"sur_{kod}.wav",f"glos_{kod}.wav"], cwd=S, check=True)
    seg,_ = M.transcribe(wav16(f"{S}/glos_{kod}.wav"), language="pl", beam_size=8,
                         word_timestamps=True, vad_filter=False, condition_on_previous_text=False)
    d = [{"s": w.word.strip(), "od": round(w.start,2), "do": round(w.end,2)} for s in seg for w in s.words]
    zm = True
    while zm:
        zm = False
        for i,x in enumerate(d):
            if x["s"].startswith(",") and i>0 and d[i-1]["s"].rstrip().isdigit():
                scal(d,i-1,i, d[i-1]["s"]+x["s"]); zm = True; break
    for x in d:
        if x["s"] == "%": x["s"] = "procent"
        if x["s"] == "płac": x["s"] = "płać"
    json.dump(d, open(f"{S}/glos_{kod}.json","w"), ensure_ascii=False)
    print(f"[{kod}] {len(d)} slow | " + " ".join(x["s"] for x in d), flush=True)
