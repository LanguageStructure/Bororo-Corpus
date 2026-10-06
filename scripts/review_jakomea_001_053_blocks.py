#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Block-level diagnostic for JAKO.001-053 against public non-Bible corpus."""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
def toks(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 return re.findall(r"[a-záéíóúâêôãõçüñ]+",s)
with W.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
wr={r["witness_id"]:r for r in rows}
raw=json.loads(P.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
units=[u for u in units if "-BM-" not in str(u.get("id","")) and "-BIB-" not in str(u.get("id",""))]
blocks=[("JAKO.001–016",1,16),("JAKO.017–053",17,53)]
for label,a,b in blocks:
 block=[wr[f"JAKO.{i:03d}"] for i in range(a,b+1)]
 q=Counter(t for r in block for t in set(toks(r["source"])) if len(t)>=5)
 scored=[]
 for u in units:
  ut=set(toks(u.get("b") or u.get("source") or ""))
  shared=[t for t in ut if t in q]
  # weighted toward less formulaic/longer lexical anchors
  score=sum((1+min(len(t),12)/12)*q[t] for t in shared)
  if shared: scored.append((score,len(shared),u,shared))
 print(f"\n=== {label} ===")
 for score,n,u,shared in sorted(scored,reverse=True,key=lambda x:(x[0],x[1]))[:20]:
  print(f"{u.get('id')} score={score:.1f} shared={n}")
  print("  anchors:",", ".join(sorted(shared,key=lambda x:(-len(x),x))[:12]))
  print("  POR:",str(u.get("p") or "").replace("\n"," ")[:260])
