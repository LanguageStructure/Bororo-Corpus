#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Locate the exceptional PB.045 across Historia Mitica, including 1-3 unit windows."""
from __future__ import annotations
import csv,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PB=ROOT/"CorBo_vNext/texts/pemo-baraedugume/pemo_baraedugume_editorial.tsv"
HM=ROOT/"CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv"
def rows(p):
 with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def score(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0
pb=next(r for r in rows(PB) if r["id"]=="PB.045"); src=pb.get("reviewed") or pb["source"]
hm=rows(HM);out=[]
for i in range(len(hm)):
 for width in (1,2,3):
  chunk=hm[i:i+width]
  if len(chunk)<width:continue
  for field in ("reviewed","witness_a","witness_b"):
   vals=[(r.get(field) or "").strip() for r in chunk]
   if not all(vals):continue
   s=score(src," ".join(vals))
   out.append((s,i,width,field," ".join(vals)))
out.sort(reverse=True,key=lambda x:x[0])
print("PB.045 — melhores alvos HM (1–3 unidades)")
print("PB BOR:",src)
print("PB PT :",pb.get("portuguese",""))
for s,i,w,f,text in out[:20]:
 ids="–".join(r["id"] for r in hm[i:i+w])
 print(f"\n{s:.3f} | {ids} | {f}")
 print(text)
