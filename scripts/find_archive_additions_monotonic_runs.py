#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find sequence-level candidate alignments for archive-additions.

For each archive document, compares each unit to each public collection and
reports monotonic runs where consecutive archive units map to increasing
public-unit positions with moderate textual support. Diagnostic only.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def sim(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0.0
with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
raw=json.loads(PUB.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
docs=defaultdict(list)
for r in rows: docs[r["document"]].append(r)
cols=defaultdict(list)
for i,u in enumerate(units):
 t=u.get("b") or u.get("source") or u.get("text") or ""
 if norm(t): cols[str(u.get("collection") or "")].append((i,str(u.get("id","")),t,str(u.get("p") or "")))
for doc,dr in docs.items():
 print("\n###",doc)
 hits=[]
 for ai,r in enumerate(dr):
  src=r.get("reviewed") or r.get("source") or ""
  for col,pu in cols.items():
   best=max(((sim(src,x[2]),x) for x in pu),default=(0.0,(0,"","","")),key=lambda z:z[0])
   if best[0]>=.40:
    s,x=best;hits.append((ai,r["id"],col,x[0],x[1],s,(r.get("portuguese") or ""),x[3]))
 # Adjacent archive hits to same collection whose global public positions rise reasonably.
 for a,b in zip(hits,hits[1:]):
  if b[0]==a[0]+1 and b[2]==a[2] and 0 < b[3]-a[3] <= 4:
   print(f"{a[1]} -> {a[4]} {a[5]:.3f} | {b[1]} -> {b[4]} {b[5]:.3f} | {a[2]}")
   print("  POR-A:",a[6].replace("\n"," ")[:260])
   print("  POR-B:",b[6].replace("\n"," ")[:260])
