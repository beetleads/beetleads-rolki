"""Mediana F0 glosu lektora - autokorelacja na ramkach dzwiecznych."""
import subprocess, sys, numpy as np
SR=16000
def wczytaj(p):
    raw=subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],
                       capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32).copy()
def f0(x):
    okno=int(0.04*SR); hop=int(0.02*SR)
    lo,hi=int(SR/300),int(SR/70)
    out=[]
    for i in range(0,len(x)-okno,hop):
        r=x[i:i+okno]
        if np.sqrt((r**2).mean())<0.02: continue
        r=r-r.mean()
        ac=np.correlate(r,r,"full")[okno-1:]
        if ac[0]<=0: continue
        ac/=ac[0]
        seg=ac[lo:hi]
        k=int(np.argmax(seg))+lo
        if ac[k]<0.35: continue
        out.append(SR/k)
    return np.array(out)
for p in sys.argv[1:]:
    v=f0(wczytaj(p))
    if len(v)<20: print(f"{p}\tza malo ramek"); continue
    print(f"{p}\tmediana {np.median(v):5.1f} Hz\tramki {len(v)}\tp25 {np.percentile(v,25):5.1f} p75 {np.percentile(v,75):5.1f}")
