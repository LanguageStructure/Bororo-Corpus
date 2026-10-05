#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnostic candidates for archive-additions against current public CorBo.

Reports the best public match for every archive unit whose normalized Bororo
similarity is >= 0.55, grouped in source order. Diagnostic only: similarity
never establishes documentary equivalence automatically.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def score(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0.0
with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
raw=json.loads(PUB.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
public=[]
for u in units:
 t=u.get("b") or u.get("source") or u.get("text") or ""
 if norm(t): public.append((str(u.get("id","")),str(u.get("collection") or ""),t,str(u.get("p") or "")))
bydoc=Counter(); shown=0
for r in rows:
 src=(r.get("reviewed") or r.get("source") or "").strip()
 best=max(((score(src,u[2]),u) for u in public),default=(0.0,("","","","")),key=lambda z:z[0])
 if best[0] < .55: continue
 s,(uid,col,bt,pt)=best
 bydoc[r["document"]]+=1; shown+=1
 print(f"{r['id']}\t{r['document']}\t{s:.3f}\t{uid}\t{col}")
 print("  A-BOR:",src.replace("\n"," ")[:500])
 print("  A-POR:",(r.get("portuguese") or "").replace("\n"," ")[:500])
 print("  C-BOR:",bt.replace("\n"," ")[:500])
 print("  C-POR:",pt.replace("\n"," ")[:500])
print("\nRESUMO")
print("candidatos >=0.55:",shown)
for k,v in sorted(bydoc.items()): print(f"{k}: {v}")
