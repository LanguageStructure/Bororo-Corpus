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
with W.open(encoding="utf-8") as f:
 rows=[r for r in csv.DictReader(f,delimiter="\t") if r["witness_id"].startswith("IPEW.")]
pub=json.loads(P.read_text(encoding="utf-8"))
blocks=[(1,15),(16,30),(31,45),(46,60)]
for lo,hi in blocks:
 rs=[r for r in rows if lo<=int(r["witness_id"].split(".")[1])<=hi]
 sb=norm(" ".join(r.get("source","") for r in rs))
 sp=norm(" ".join(r.get("portuguese","") for r in rs))
 cand=[]
 for u in pub:
  ub,up=norm(u.get("b","")),norm(u.get("p",""))
  if not ub or not up: continue
  br=SequenceMatcher(None,sb,ub,autojunk=False).ratio()
  pr=SequenceMatcher(None,sp,up,autojunk=False).ratio()
  cand.append(((br*pr)**0.5,br,pr,u.get("id",""),up))
 cand.sort(reverse=True)
 print(f"\n=== IPEW.{lo:03d}–{hi:03d} ===")
 print("IPEW-POR:", " ".join(r.get("portuguese","").replace("\\n"," ") for r in rs)[:1800])
 for score,br,pr,uid,up in cand[:6]:
  print(f"[{uid}] balanced={score:.3f} bor={br:.3f} por={pr:.3f}")
  print("PUB-POR:",up[:320])
