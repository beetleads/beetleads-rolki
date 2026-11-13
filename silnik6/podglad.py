import json, sys, silnik6 as s6, sceny_b2b
from PIL import Image
for k in sys.argv[1:]:
    r=json.load(open(f"rolka_{k}w.json")); sl=json.load(open(r["slowa"])); akc=s6.hexk(r["akcent"])
    def cs(spec):
        tx,_,nr=spec.partition("#"); nr=int(nr or 1); c=0
        for s in sl:
            if s["s"].strip(".,?!:„”").lower()==tx.lower().strip(".,?!:"):
                c+=1
                if c==nr: return s["od"]
        raise SystemExit(f"{k} brak {spec}")
    sc=r["sceny"]; st=[0 if s["od"]==0 else cs(s["od"])-0.08 for s in sc]; st.append(sl[-1]["do"]+0.6)
    assert all(b>a for a,b in zip(st,st[1:])), f"{k} kolejnosc {st}"
    tiles=[]
    for i,s in enumerate(sc[:-1]):
        for f in (0.15,0.95):
            od,do=st[i],st[i+1]; t=(do-od)*f
            im=Image.new("RGBA",(s6.W,s6.H),(40,40,48,255))
            s6.SCENY[s["typ"]](im,t,do-od,s,{"akcent":akc,"czas_slowa":cs,"od":od})
            tiles.append(im.convert("RGB").resize((270,480)))
    sh=Image.new("RGB",(270*len(tiles),480)); [sh.paste(x,(i*270,0)) for i,x in enumerate(tiles)]
    sh.save(f"/tmp/claude-0/-home-claude/2dbe75ca-4db3-575f-9da9-3016388c7a29/scratchpad/pod_{k}.jpg")
    print(k,[round(x,2) for x in st])
