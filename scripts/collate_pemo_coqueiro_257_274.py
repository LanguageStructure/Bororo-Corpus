#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused backward collation for Pemo-Coqueiro PC.257-274 against Historia Mitica.

Tests every HM unit and 2-3-unit HM windows. Prints top candidates and Portuguese
context. Diagnostic only; writes nothing.
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
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s);return " ".join(s.split())
def sim(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0
def num(s):
 m=re.search(r"(\d+)$",str(s or ""));return int(m.group(1)) if m else None
with PC.open(encoding="utf-8",newline="") as f:
 pc=[r for r in csv.DictReader(f,delimiter="\t") if num(r["id"]) is not None and 257<=num(r["id"])<=274]
data=json.loads(PUB.read_text(encoding="utf-8")); units=data if isinstance(data,list) else data.get("units",[])
hm={}
for u in units:
 m=re.search(r"HM001-u(\d+)$",str(u.get("id","")))
 if m:hm[int(m.group(1))]=u
windows=[]
for start in sorted(hm):
 for w in (1,2,3):
  ns=list(range(start,start+w))
  if all(n in hm for n in ns):
   bor=" ".join(str(hm[n].get("b") or hm[n].get("source") or "") for n in ns)
   por=" ".join(str(hm[n].get("p") or hm[n].get("portuguese") or hm[n].get("translation_pt") or "") for n in ns)
   windows.append((ns,bor,por))
print("PEMO–COQUEIRO PC.257–274 × HISTÓRIA MÍTICA — COLAÇÃO RETROATIVA")
print("Top 3 candidatos por unidade; diagnóstico somente.\n")
for r in pc:
 src=r.get("reviewed") or r.get("source") or ""
 scores=sorted(((sim(src,b),ns,b,p) for ns,b,p in windows),reverse=True,key=lambda x:x[0])[:3]
 print("="*104)
 print(f"{r['id']} | PT: {r.get('portuguese','')}")
 for rank,(s,ns,b,p) in enumerate(scores,1):
  ids="+".join(f"u{n:03d}" for n in ns)
  print(f"  {rank}. HM {ids} [{s:.3f}]")
  print(f"     BOR: {b}")
  if p: print(f"     PT : {p}")
