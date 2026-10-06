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

with W.open(encoding="utf-8") as f:
 rows=[r for r in csv.DictReader(f,delimiter="\t") if r["witness_id"].startswith("FAC.")]
pub=json.loads(P.read_text(encoding="utf-8"))
if isinstance(pub,dict):
 for k in ("units","items","data"):
  if isinstance(pub.get(k),list): pub=pub[k]; break

def val(r,*keys):
 for k in keys:
  if r.get(k): return str(r[k])
 return ""

# Exclude this staged witness itself; public corpus currently does not contain it.
docs={}
df=Counter()
for r in pub:
 pid=val(r,"id","unit_id")
 bor=val(r,"bororo","text","source","reviewed")
 if not pid or not bor: continue
 bag=set(toks(bor)); docs[pid]=(r,bor,bag)
 for t in bag: df[t]+=1
inv=defaultdict(set)
for pid,(_,_,bag) in docs.items():
 for t in bag:
  if df[t]<=12: inv[t].add(pid)

print("FAC units:",len(rows))
for r in rows:
 src=r["source"]; st=set(toks(src)); cand=defaultdict(list)
 for t in st:
  for pid in inv.get(t,()): cand[pid].append(t)
 scored=[]
 for pid,shared in cand.items():
  rr,bor,bag=docs[pid]
  rare=[t for t in shared if df[t]<=4]
  unique=[t for t in shared if df[t]==1]
  lex=sum(1/df[t] for t in shared)
  sim=SequenceMatcher(None,norm(src),norm(bor),autojunk=False).ratio()
  pt=SequenceMatcher(None,norm(r.get("portuguese","")),norm(val(rr,"portuguese","text_por","translation")),autojunk=False).ratio()
  # names/rare anchors dominate; similarity is supporting evidence only.
  score=lex+1.5*len(unique)+0.5*len(rare)+2*sim+pt
  if len(rare)>=2 or unique or sim>=0.55: scored.append((score,sim,pt,pid,shared,rr,bor))
 scored.sort(reverse=True,key=lambda x:x[0])
 print("\n===",r["witness_id"],"===")
 print("SECTION:",r.get("section",""))
 print("FAC-BOR:",src.replace("\\n"," "))
 print("FAC-POR:",r.get("portuguese","").replace("\\n"," "))
 if not scored:
  print("NO DISTINCTIVE PUBLIC CANDIDATE")
  continue
 for score,sim,pt,pid,shared,rr,bor in scored[:4]:
  anchors=sorted(shared,key=lambda t:(df[t],-len(t),t))
  print(f"\n[{pid}] score={score:.2f} bor={sim:.3f} por={pt:.3f}")
  print("ANCHORS:","; ".join(f"{t}(df={df[t]})" for t in anchors[:14]))
  print("PUB-BOR:",bor.replace("\\n"," ")[:900])
  print("PUB-POR:",val(rr,"portuguese","text_por","translation").replace("\\n"," ")[:900])
