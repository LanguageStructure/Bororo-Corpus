#!/usr/bin/env python3
import csv,json,re,unicodedata
from pathlib import Path
from difflib import SequenceMatcher
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
def norm(s):
 if not isinstance(s,str): s=""
 s=unicodedata.normalize("NFC",s).lower()
 s=s.replace("\\n"," ")
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
with W.open(encoding="utf-8") as f: wr=list(csv.DictReader(f,delimiter="\t"))
pub=json.loads(P.read_text(encoding="utf-8"))
rows={r["witness_id"]:r for r in wr if r["witness_id"].startswith("AROC.")}
blocks=[("AROC.018–030",18,30),("AROC.031–041",31,41),("AROC.042–046",42,46)]
for label,a,b in blocks:
 ar=[rows[f"AROC.{i:03d}"] for i in range(a,b+1)]
 bor=norm(" ".join(r.get("source","") for r in ar))
 por=norm(" ".join(r.get("portuguese","") for r in ar))
 scored=[]
 for u in pub:
  ub=norm(u.get("bororo") or u.get("reviewed") or u.get("source") or u.get("text") or "")
  up=norm(u.get("portuguese") or u.get("text_por") or "")
  if not ub: continue
  # block-to-unit diagnostic: semantic PT support is required
  bs=SequenceMatcher(None,bor,ub,autojunk=False).ratio()
  ps=SequenceMatcher(None,por,up,autojunk=False).ratio() if up else 0
  if ps<0.16: continue
  score=bs+ps
  scored.append((score,bs,ps,u.get("id",""),up[:220]))
 scored.sort(reverse=True)
 print("\n===",label,"===")
 print("AROC-POR:", " ".join(r.get("portuguese","") for r in ar)[:500])
 for score,bs,ps,uid,upt in scored[:5]:
  print(f"[{uid}] total={score:.3f} bor={bs:.3f} por={ps:.3f}")
  print("PUB-POR:",upt)
