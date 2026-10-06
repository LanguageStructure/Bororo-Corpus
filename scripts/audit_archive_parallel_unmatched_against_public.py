#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fast re-audit of unmatched archive parallel witnesses against public CorBo."""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def toks(s): return set(s.split())
with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
raw=json.loads(PUB.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
unmatched=[r for r in rows if (r.get("collation_status") or "").strip()=="unmatched"]
P=[]; exact_idx=defaultdict(list); inv=defaultdict(list)
for u in units:
 n=norm(u.get("b") or u.get("source") or u.get("text") or "")
 if not n: continue
 pi=len(P);P.append((n,u));exact_idx[n].append(u)
 for w in toks(n):inv[w].append(pi)
exact=[];near=[]
for r in unmatched:
 n=norm(r.get("source") or "")
 if n in exact_idx:
  for u in exact_idx[n]:exact.append((r,u,1.0))
  continue
 votes=Counter()
 for w in toks(n):
  for pi in inv.get(w,()):votes[pi]+=1
 # Exact/0.99 matches necessarily share substantial vocabulary; shortlist 160.
 for pi,_ in votes.most_common(160):
  pn,u=P[pi]
  lr=len(n)/len(pn)
  if lr<.80 or lr>1.25:continue
  s=SequenceMatcher(None,n,pn,autojunk=True).ratio()
  if s>=.99:near.append((r,u,s));break
matched={r["witness_id"] for r,_,_ in exact+near}
print("Archive parallel unmatched auditadas:",len(unmatched))
print("Corpus público:",len(units))
print("exact:",len(exact))
print("near_exact >=0.99:",len(near))
print("sem duplicata forte:",len(unmatched)-len(matched))
for label,data in (("EXACT",exact),("NEAR",near)):
 if data:
  print("\n"+label)
  for r,u,s in data:
   print(f"{r['witness_id']}\t{r['document']}\t{s:.3f}\t{u.get('id','')}\t{u.get('collection','')}")
