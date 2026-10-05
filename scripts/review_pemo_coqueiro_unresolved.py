#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final diagnostic for unresolved Pemo-Coqueiro collation rows.
Read-only: shows PC context and top HM candidates.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PC=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"
COL=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_collation.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def sim(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0.0
def num(s):
 m=re.search(r"(\d+)$",str(s or "")); return int(m.group(1)) if m else None
with PC.open(encoding="utf-8",newline="") as f:
 rows=list(csv.DictReader(f,delimiter="\t"))
by_n={num(r["id"]):r for r in rows}
with COL.open(encoding="utf-8",newline="") as f:
 unresolved=[num(r["id"]) for r in csv.DictReader(f,delimiter="\t") if r["status"]=="unresolved"]
raw=json.loads(PUB.read_text(encoding="utf-8"))
units=raw if isinstance(raw,list) else raw.get("units",[])
hm={}
for u in units:
 m=re.search(r"HM001-u(\d+)$",str(u.get("id","")))
 if m: hm[int(m.group(1))]=u
wins=[]
for start in sorted(hm):
 for width in (1,2,3):
  ns=list(range(start,start+width))
  if all(x in hm for x in ns):
   b=" ".join(str(hm[x].get("b") or hm[x].get("source") or "") for x in ns)
   p=" ".join(str(hm[x].get("p") or hm[x].get("portuguese") or hm[x].get("translation_pt") or "") for x in ns)
   wins.append((ns,b,p))
for x in unresolved:
 r=by_n[x]; src=r.get("reviewed") or r.get("source") or ""
 print("="*110)
 print(f"{r['id']} | BOR: {src}")
 print(f"PT: {r.get('portuguese','')}")
 for y,label in ((x-1,"PREV"),(x+1,"NEXT")):
  if y in by_n:
   q=by_n[y]
   print(f"{label} {q['id']} | {q.get('reviewed') or q.get('source') or ''}")
   print(f"{label} PT: {q.get('portuguese','')}")
 scores=sorted(((sim(src,b),ns,b,p) for ns,b,p in wins),reverse=True,key=lambda z:z[0])[:3]
 for rank,(s,ns,b,p) in enumerate(scores,1):
  ids="+".join(f"u{z:03d}" for z in ns)
  print(f"HM{rank} {ids} [{s:.3f}] | {b}")
  if p: print(f"HM{rank} PT: {p}")
