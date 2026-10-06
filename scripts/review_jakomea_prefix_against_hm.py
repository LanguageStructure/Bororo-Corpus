#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contextual diagnostic for JAKO.001-070 against História Mítica before u085."""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s);return " ".join(s.split())
def tok(s):return set(norm(s).split())
with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
j=[r for r in rows if r["witness_id"].startswith("JAKO.") and int(r["witness_id"].split(".")[1])<=70]
raw=json.loads(PUB.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
hm=[]
for u in units:
 uid=str(u.get("id",""))
 m=re.fullmatch(r"BOR-CORBO-HM001-u(\d+)",uid)
 if m and int(m.group(1))<85:
  hm.append((int(m.group(1)),uid,norm(u.get("b") or u.get("source") or ""),str(u.get("p") or "")))
inv=defaultdict(list)
for k,x in enumerate(hm):
 for w in tok(x[2]):inv[w].append(k)
print(f"JAKO auditadas: {len(j)}; HM anteriores a u085: {len(hm)}")
best=[]
for r in j:
 n=norm(r["source"]);votes=Counter()
 for w in tok(n):
  for k in inv.get(w,()):votes[k]+=1
 cand=[]
 for k,_ in votes.most_common(40):
  h=hm[k];s=SequenceMatcher(None,n,h[2],autojunk=True).ratio()
  cand.append((s,h))
 if cand:
  s,h=max(cand,key=lambda z:z[0]);best.append((r,s,h))
for r,s,h in best:
 if s>=.45:
  print(f"{r['witness_id']}\t{s:.3f}\t{h[1]}")
  print("  J-POR:",(r.get("portuguese") or "").replace("\n"," ")[:350])
  print("  H-POR:",h[3].replace("\n"," ")[:350])
# report monotonicity among best candidates >= .35
seq=[(int(r["witness_id"].split(".")[1]),h[0],s) for r,s,h in best if s>=.35]
runs=[]
cur=[]
for x in seq:
 if not cur or (x[0]>cur[-1][0] and x[1]>=cur[-1][1] and x[1]-cur[-1][1]<=5):cur.append(x)
 else:
  if len(cur)>=3:runs.append(cur)
  cur=[x]
if len(cur)>=3:runs.append(cur)
print("\nRUNS")
for run in runs:print(f"JAKO.{run[0][0]:03d}..JAKO.{run[-1][0]:03d} -> HM u{run[0][1]:03d}..u{run[-1][1]:03d} ({len(run)} hits)")
