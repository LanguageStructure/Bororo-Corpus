#!/usr/bin/env python3
import csv,json,re,unicodedata
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",s or "").lower().replace("\\n"," ")
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def toks(s): return [x for x in norm(s).split() if len(x)>=4]
def val(r,*ks):
 for k in ks:
  if r.get(k): return str(r[k])
 return ""
with W.open(encoding="utf-8") as f:
 rows=[r for r in csv.DictReader(f,delimiter="\t") if r["witness_id"].startswith("AROC.")]
raw=json.loads(P.read_text(encoding="utf-8"))
pub=raw if isinstance(raw,list) else next((raw[k] for k in ("units","items","data") if isinstance(raw.get(k),list)),[])
docs={}; df=Counter()
for r in pub:
 pid=val(r,"id","unit_id"); bor=val(r,"b","bororo","text","source","reviewed")
 if not pid or not bor: continue
 bag=set(toks(bor)); docs[pid]=(r,bor,bag)
 for t in bag: df[t]+=1
inv=defaultdict(set)
for pid,(_,_,bag) in docs.items():
 for t in bag:
  if df[t]<=15: inv[t].add(pid)
print("AROC units:",len(rows))
for r in rows:
 src=r["source"]; st=set(toks(src)); cand=defaultdict(set)
 for t in st:
  for pid in inv.get(t,()): cand[pid].add(t)
 scored=[]
 for pid,shared in cand.items():
  rr,bor,_=docs[pid]
  rare=[t for t in shared if df[t]<=4]; unique=[t for t in shared if df[t]==1]
  sim=SequenceMatcher(None,norm(src),norm(bor),autojunk=False).ratio()
  ptxt=val(rr,"p","portuguese","text_por","translation")
  pt=SequenceMatcher(None,norm(r.get("portuguese","")),norm(ptxt),autojunk=False).ratio() if ptxt else 0
  lex=sum(1/df[t] for t in shared)
  score=lex+1.5*len(unique)+0.5*len(rare)+2*sim+1.5*pt
  if unique or len(rare)>=2 or sim>=.45 or pt>=.35:
   scored.append((score,sim,pt,pid,shared))
 scored.sort(reverse=True,key=lambda x:x[0])
 print("\n===",r["witness_id"],"===")
 print("AROC-POR:",r.get("portuguese","").replace("\\n"," "))
 if not scored: print("NO DISTINCTIVE PUBLIC CANDIDATE"); continue
 for score,sim,pt,pid,shared in scored[:4]:
  a=sorted(shared,key=lambda t:(df[t],-len(t),t))
  print(f"[{pid}] score={score:.2f} bor={sim:.3f} por={pt:.3f} anchors="+",".join(f"{t}:{df[t]}" for t in a[:10]))
