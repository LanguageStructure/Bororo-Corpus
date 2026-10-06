#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-audit unmatched archive parallel witnesses against current public CorBo.

Read-only diagnostic. Existing confirmed/component decisions remain authoritative.
Reports exact and near-exact matches only; no automatic status changes.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
raw=json.loads(PUB.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
idx={}
for u in units:
 t=u.get("b") or u.get("source") or u.get("text") or ""; n=norm(t)
 if n: idx.setdefault(n,[]).append(u)
unmatched=[r for r in rows if (r.get("collation_status") or "").strip()=="unmatched"]
exact=[]; near=[]
pub=[(norm(u.get("b") or u.get("source") or u.get("text") or ""),u) for u in units]
for r in unmatched:
 n=norm(r.get("source") or "")
 if n in idx:
  for u in idx[n]: exact.append((r,u,1.0))
  continue
 # expensive similarity only after cheap length filtering
 cand=[]
 for pn,u in pub:
  if not pn: continue
  ratio=len(n)/len(pn) if pn else 0
  if ratio < .80 or ratio > 1.25: continue
  s=SequenceMatcher(None,n,pn,autojunk=True).ratio()
  if s>=.99:cand.append((s,u))
 if cand:
  s,u=max(cand,key=lambda x:x[0]);near.append((r,u,s))
print("Archive parallel unmatched auditadas:",len(unmatched))
print("exact:",len(exact))
print("near_exact >=0.99:",len(near))
print("sem duplicata forte:",len(unmatched)-len({r["witness_id"] for r,_,_ in exact+near}))
for label,data in [("EXACT",exact),("NEAR",near)]:
 if data:
  print("\n"+label)
  for r,u,s in data:
   print(f"{r['witness_id']}\t{r['document']}\t{s:.3f}\t{u.get('id','')}\t{u.get('collection','')}")
