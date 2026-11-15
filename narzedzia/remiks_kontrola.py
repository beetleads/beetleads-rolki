#!/usr/bin/env python3
"""Kontrola remiksu: obraz nietkniety, poziomy, muzyka glosniej, tekst lektora bez zmian."""
import subprocess, sys, json, os, re
import numpy as np
from scipy.io import wavfile

def vmd5(p):
    o = subprocess.run(["ffmpeg","-v","error","-i",p,"-map","0:v","-c","copy","-f","md5","-"],
                       capture_output=True,text=True).stdout.strip()
    return o.replace("MD5=","")

def info(p):
    o = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height,r_frame_rate,sample_rate",
                        "-of","json",p],capture_output=True,text=True).stdout
    j = json.loads(o); st = {s["codec_type"]: s for s in j["streams"]}
    return float(j["format"]["duration"]), st

def poziomy(p):
    e = subprocess.run(["ffmpeg","-v","info","-nostats","-i",p,"-af","ebur128=peak=true:framelog=quiet","-f","null","-"],
                       capture_output=True,text=True).stderr
    I = [l for l in e.splitlines() if l.strip().startswith("I:")]
    TP = [l for l in e.splitlines() if "Peak:" in l]
    return float(I[-1].split()[1]), float(TP[-1].split()[-2]) if TP else None

def wav(p, sr=44100):
    t = "/tmp/_k.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",p,"-vn","-ac","1","-ar",str(sr),t],check=True)
    s, x = wavfile.read(t)
    return x.astype(np.float32)/32768.0

def muzyka_db(a, b, okna, sr=44100):
    """o ile zmienil sie poziom w pauzach mowy (tam slychac sam podklad)"""
    out=[]
    for s0,s1 in okna:
        i,j=int(s0*sr),int(s1*sr)
        if j-i<1000 or j>min(len(a),len(b)): continue
        ra=np.sqrt((a[i:j]**2).mean())+1e-9; rb=np.sqrt((b[i:j]**2).mean())+1e-9
        out.append(20*np.log10(rb/ra))
    return round(float(np.median(out)),2) if out else None

def pauzy(x, sr=44100, prog_db=-34):
    k=int(0.05*sr); r=np.sqrt(np.convolve(x**2,np.ones(k)/k,"same"))
    db=20*np.log10(r+1e-9); db-=db.max()
    cicho=db<prog_db; odc=[];st=None
    for i,c in enumerate(np.r_[cicho,False]):
        if c and st is None: st=i
        elif not c and st is not None:
            if (i-st)/sr>0.30: odc.append((st/sr+0.05,i/sr-0.05))
            st=None
    return odc

def tekst(p, model=[None]):
    from faster_whisper import WhisperModel
    if model[0] is None: model[0]=WhisperModel("small", device="cpu", compute_type="int8")
    x=wav(p,16000)
    segs,_=model[0].transcribe(x.astype(np.float32), language="pl", beam_size=5)
    t=" ".join(s.text for s in segs)
    return re.sub(r"[^a-ząćęłńóśźż0-9 ]","",t.lower()).split()

def main(orig, nowy, z_tekstem="1"):
    d1,s1=info(orig); d2,s2=info(nowy)
    w={}
    w["obraz_identyczny"]= vmd5(orig)==vmd5(nowy)
    w["czas"]=[round(d1,2),round(d2,2)]
    w["rozdz"]=f'{s2["video"]["width"]}x{s2["video"]["height"]}'
    w["fps"]=s2["video"]["r_frame_rate"]
    i1,t1=poziomy(orig); i2,t2=poziomy(nowy)
    w["LUFS"]=[i1,i2]; w["TP"]=[t1,t2]
    a,b=wav(orig),wav(nowy)
    pz=pauzy(a)
    w["muzyka_dB"]=muzyka_db(a,b,pz)
    if z_tekstem=="1":
        ta,tb=tekst(orig),tekst(nowy)
        w["slowa"]=[len(ta),len(tb)]
        w["tekst_bez_zmian"]= ta==tb
        if ta!=tb:
            w["roznica"]=[x for x in ta if x not in tb][:8]+["|"]+[x for x in tb if x not in ta][:8]
    print(json.dumps(w,ensure_ascii=False))

if __name__=="__main__": main(*sys.argv[1:])
