#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused collation of Pemo-Coqueiro PC.001-039 against Historia Mitica.
Diagnostic only; writes nothing.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PC=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"
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
 rows=[r for r in csv.DictReader(f,delimiter="\t") if num(r["id"]) and 1<=num(r["id"])<=39]
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
print("PEMO–COQUEIRO PC.001–039 × HISTÓRIA MÍTICA")
print("Top 3 candidatos; diagnóstico somente.\n")
anchors=[]
for r in rows:
 src=r.get("reviewed") or r.get("source") or ""
 scores=sorted(((sim(src,b),ns,b,p) for ns,b,p in wins),reverse=True,key=lambda z:z[0])[:3]
 if scores and scores[0][0]>=.70: anchors.append((r["id"],scores[0][1],scores[0][0]))
 print("="*104)
 print(f"{r['id']} | BOR: {src}")
 print(f"PT: {r.get('portuguese','')}")
 for rank,(s,ns,b,p) in enumerate(scores,1):
  ids="+".join(f"u{x:03d}" for x in ns)
  print(f"  {rank}. HM {ids} [{s:.3f}]")
  print(f"     BOR: {b}")
  if p: print(f"     PT : {p}")
print("\n"+"#"*104)
print("ÂNCORAS >= 0.70 (não são confirmação automática)")
for pid,ns,s in anchors:
 print(f"{pid} => "+ "+".join(f"u{x:03d}" for x in ns)+f" [{s:.3f}]")
