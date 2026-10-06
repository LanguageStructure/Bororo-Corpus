#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fast sequence diagnostic for archive-additions against public CorBo.

Uses an inverted token index to shortlist plausible public units, then applies
SequenceMatcher only to those candidates. Diagnostic only.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def toks(s): return set(norm(s).split())
def simn(a,b):
 return SequenceMatcher(None,a,b,autojunk=True).ratio() if a and b else 0.0
with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
raw=json.loads(PUB.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
P=[]; inv=defaultdict(list)
for i,u in enumerate(units):
 t=u.get("b") or u.get("source") or u.get("text") or ""; n=norm(t)
 if not n: continue
 rec=(i,str(u.get("id","")),str(u.get("collection") or ""),n,str(u.get("p") or ""))
 pi=len(P);P.append(rec)
 for w in toks(n): inv[w].append(pi)
docs=defaultdict(list)
for r in rows: docs[r["document"]].append(r)
for doc,dr in docs.items():
 print("\n###",doc)
 per=[]
 for ai,r in enumerate(dr):
  srcn=norm(r.get("reviewed") or r.get("source") or ""); st=toks(srcn)
  votes=Counter()
  for w in st:
   for pi in inv.get(w,()): votes[pi]+=1
  # shortlist by shared-token count; cap keeps runtime bounded
  shortlist=[pi for pi,_ in votes.most_common(120)]
  hits=[]
  for pi in shortlist:
   pos,uid,col,pn,pt=P[pi]
   s=simn(srcn,pn)
   if s>=.40: hits.append((s,pos,uid,col,pt))
  # retain a few best hits per collection
  bycol=defaultdict(list)
  for h in hits: bycol[h[3]].append(h)
  kept=[]
  for col,hs in bycol.items():
   kept.extend(sorted(hs,reverse=True)[:3])
  per.append((r,kept))
 for ai in range(len(per)-1):
  r1,h1=per[ai];r2,h2=per[ai+1]
  seen=set()
  for a in h1:
   for b in h2:
    if a[3]!=b[3]: continue
    gap=b[1]-a[1]
    if not (0 < gap <= 4): continue
    key=(a[2],b[2])
    if key in seen: continue
    seen.add(key)
    print(f"{r1['id']} -> {a[2]} {a[0]:.3f} | {r2['id']} -> {b[2]} {b[0]:.3f} | {a[3]}")
    print("  POR-A:",(r1.get("portuguese") or "").replace("\n"," ")[:260])
    print("  POR-B:",(r2.get("portuguese") or "").replace("\n"," ")[:260])
