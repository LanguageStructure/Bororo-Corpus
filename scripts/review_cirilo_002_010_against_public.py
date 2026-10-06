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
 rows=[r for r in csv.DictReader(f,delimiter="\t") if re.fullmatch(r"CIR\.00[2-9]|CIR\.010",r["witness_id"])]
pub=json.loads(P.read_text(encoding="utf-8"))
for r in rows:
 sb,sp=norm(r.get("source","")),norm(r.get("portuguese",""))
 cand=[]
 for u in pub:
  ub,up=norm(u.get("b","")),norm(u.get("p",""))
  if not ub or not up: continue
  br=SequenceMatcher(None,sb,ub,autojunk=False).ratio()
  pr=SequenceMatcher(None,sp,up,autojunk=False).ratio()
  score=(br*pr)**0.5
  cand.append((score,br,pr,u.get("id",""),up))
 cand.sort(reverse=True)
 print("\n===",r["witness_id"],"===")
 print("CIR-POR:",r.get("portuguese","").replace("\\n"," "))
 for score,br,pr,uid,up in cand[:5]:
  print(f"[{uid}] balanced={score:.3f} bor={br:.3f} por={pr:.3f}")
  print("PUB-POR:",up[:450])
