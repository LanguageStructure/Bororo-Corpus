#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sequence-aware collation diagnostic for Pemo-Coqueiro vs public Historia Mitica.

Strong textual matches (exact or >= .99) are anchors only. Unmatched rows are
tested inside monotonic HM intervals and 1-3-unit HM windows. No files are changed.
"""
from __future__ import annotations
import csv,re,unicodedata,json
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PC=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"
PUBLIC=ROOT/"docs/data/corbo-units.json"

def read_tsv(p):
 with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold().replace("\\n"," ")
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def sim(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0.0
def pcnum(x):
 m=re.search(r"(\d+)$",x or "");return int(m.group(1)) if m else None
def hmnum(x):
 m=re.search(r"HM001-u(\d+)$",x or "");return int(m.group(1)) if m else None

pc=read_tsv(PC)
data=json.loads(PUBLIC.read_text(encoding="utf-8"))
units=data if isinstance(data,list) else data.get("units",[])
hm=[u for u in units if hmnum(str(u.get("id",""))) is not None]
hm.sort(key=lambda u:hmnum(str(u["id"])))
by_n={hmnum(str(u["id"])):u for u in hm}

anchors=[]
for r in pc:
 src=r.get("reviewed") or r.get("source") or ""
 best=None
 for u in hm:
  for field in ("b","source"):
   val=u.get(field) or ""
   if norm(src)==norm(val) and norm(src):
    best=(1.0,u,field);break
   # only compute near-exact when lengths can possibly reach .99
   a,b=norm(src),norm(val)
   if a and b and max(len(a),len(b))/min(len(a),len(b))<=1.021:
    s=sim(a,b)
    if s>=.99 and (best is None or s>best[0]):best=(s,u,field)
  if best and best[0]==1.0:break
 if best:anchors.append((pcnum(r["id"]),hmnum(str(best[1]["id"])),best[0],r["id"],best[1]["id"]))

print("PEMO–COQUEIRO × HISTÓRIA MÍTICA — ÂNCORAS E INTERVALOS")
print(f"âncoras fortes: {len(anchors)}")
print("Nenhuma correspondência abaixo de 0.99 é gravada automaticamente.\n")
for a in anchors:print(f"ANCHOR {a[3]} => {a[4]} [{a[2]:.3f}]")

# Monotonic neighboring anchors define expected HM interval.
print("\nCANDIDATOS DIAGNÓSTICOS ENTRE ÂNCORAS")
found=0
for idx,r in enumerate(pc):
 pn=pcnum(r["id"])
 if any(a[0]==pn for a in anchors):continue
 prev=[a for a in anchors if a[0]<pn]
 nxt=[a for a in anchors if a[0]>pn]
 if not prev or not nxt:continue
 left=max(prev,key=lambda x:x[0]);right=min(nxt,key=lambda x:x[0])
 if left[1]>=right[1]:continue
 lo,hi=left[1]+1,right[1]-1
 if hi<lo:continue
 src=r.get("reviewed") or r.get("source") or ""
 scores=[]
 # 1-3 consecutive HM units, constrained by anchor interval
 for start in range(lo,hi+1):
  for w in (1,2,3):
   nums=list(range(start,start+w))
   if nums[-1]>hi or not all(n in by_n for n in nums):continue
   text=" ".join(str(by_n[n].get("b") or by_n[n].get("source") or "") for n in nums)
   scores.append((sim(src,text),nums,text))
 if not scores:continue
 score,nums,text=max(scores,key=lambda x:x[0])
 # surface useful diagnostics, not decisions
 if score>=.60:
  found+=1
  ids="–".join(str(by_n[n]["id"]) for n in nums)
  print("\n"+"="*96)
  print(f"{r['id']} => {ids} [{score:.3f}] | anchors {left[3]}→{left[4]} / {right[3]}→{right[4]}")
  print("PC BOR:",src.replace("\n"," "))
  print("PC PT :",str(r.get("portuguese") or "").replace("\n"," "))
  print("HM BOR:",text.replace("\n"," "))
print(f"\nCandidatos >=0.60 entre âncoras: {found}")
