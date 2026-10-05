#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expand manually plausible Pemo-Coqueiro blocks around monotonic HM anchors.

Tests PC units in selected documentary blocks against nearby HM units and 1-3-unit
windows. Diagnostic only; no corpus/staging file is modified.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PC=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
BLOCKS=[
 ("PC184-189 / HM146-151",184,189,146,151),
 ("PC224-231 / HM146-151",224,231,146,151),
 ("PC240-242 / HM148-151",240,242,148,151),
 ("PC252-253 / HM176-177",252,253,176,177),
 ("PC255-256 / HM140-141",255,256,140,141),
 ("PC275-276 / HM137-138",275,276,137,138),
]
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s);return " ".join(s.split())
def sim(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0
def num(s):
 m=re.search(r"(\d+)$",s or "");return int(m.group(1)) if m else None
with PC.open(encoding="utf-8",newline="") as f: pc=list(csv.DictReader(f,delimiter="\t"))
data=json.loads(PUB.read_text(encoding="utf-8")); units=data if isinstance(data,list) else data.get("units",[])
hm={}
for u in units:
 m=re.search(r"HM001-u(\d+)$",str(u.get("id","")))
 if m:hm[int(m.group(1))]=u
for title,plo,phi,hlo,hhi in BLOCKS:
 print("\n"+"#"*100);print(title)
 for r in pc:
  pn=num(r["id"])
  if pn is None or not (plo<=pn<=phi):continue
  src=r.get("reviewed") or r.get("source") or ""
  scores=[]
  # allow one HM unit of contextual margin around proposed block
  for start in range(max(1,hlo-1),hhi+2):
   for w in (1,2,3):
    ns=list(range(start,start+w))
    if ns[-1]>hhi+1 or not all(n in hm for n in ns):continue
    text=" ".join(str(hm[n].get("b") or hm[n].get("source") or "") for n in ns)
    scores.append((sim(src,text),ns,text))
  scores.sort(reverse=True,key=lambda x:x[0])
  s,ns,text=scores[0]
  ids="–".join(str(hm[n]["id"]) for n in ns)
  print("\n"+"="*96)
  print(f"{r['id']} => {ids} [{s:.3f}]")
  print("PC BOR:",src.replace("\n"," "))
  print("PC PT :",str(r.get("portuguese") or "").replace("\n"," "))
  print("HM BOR:",text.replace("\n"," "))
