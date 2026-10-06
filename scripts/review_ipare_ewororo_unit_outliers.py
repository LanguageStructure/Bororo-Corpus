#!/usr/bin/env python3
import csv,json,re,unicodedata
from pathlib import Path
from difflib import SequenceMatcher
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
def norm(x):
 if not isinstance(x,str): return ""
 x=unicodedata.normalize("NFC",x).lower().replace("\\n"," ")
 x=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",x)
 return " ".join(x.split())
with W.open(encoding="utf-8") as f: rows=[r for r in csv.DictReader(f,delimiter="\t") if r["witness_id"].startswith("IPEW.")]
pub=json.loads(P.read_text(encoding="utf-8"))
out=[]
for r in rows:
 sb,sp=norm(r.get("source","")),norm(r.get("portuguese",""))
 best=None
 for u in pub:
  ub,up=norm(u.get("b","")),norm(u.get("p",""))
  if not ub or not up: continue
  br=SequenceMatcher(None,sb,ub,autojunk=False).ratio(); pr=SequenceMatcher(None,sp,up,autojunk=False).ratio()
  score=(br*pr)**0.5
  x=(score,br,pr,u.get("id",""),up)
  if best is None or x>best: best=x
 if best and best[0]>=0.48: out.append((r,best))
print("IPEW units:",len(rows)); print("unit outliers >=0.48:",len(out))
for r,(s,b,p,uid,pt) in out:
 print("\n===",r["witness_id"],"==="); print("IPEW-POR:",r.get("portuguese","").replace("\\n"," "))
 print(f"[{uid}] balanced={s:.3f} bor={b:.3f} por={p:.3f}"); print("PUB-POR:",pt[:500])
