#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rare-token/name diagnostic for JAKO.001-070 against complete public CorBo."""
from __future__ import annotations
import csv,json,re,unicodedata
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 return re.findall(r"[a-záéíóúâêôãõçüñ]+",s)
with W.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
j=[r for r in rows if re.fullmatch(r"JAKO\.0(?:[0-6]\d|70)",r["witness_id"])]
raw=json.loads(P.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
post=defaultdict(list);freq=Counter()
for u in units:
 ws=set(norm(u.get("b") or u.get("source") or ""))
 for w in ws:
  freq[w]+=1;post[w].append(u)
# Ignore frequent grammatical/formulaic vocabulary; report rare shared tokens.
for r in j:
 shared=[]
 for w in set(norm(r["source"])):
  if len(w)>=5 and 0<freq[w]<=8:
   shared.append((freq[w],w,post[w]))
 if not shared:continue
 shared.sort(key=lambda x:(x[0],-len(x[1]),x[1]))
 print(f"\n[{r['witness_id']}] {r.get('portuguese','').replace(chr(10),' ')[:220]}")
 seen=set()
 for n,w,us in shared[:10]:
  ids=[]
  for u in us:
   uid=str(u.get("id",""))
   if uid not in seen:
    ids.append(uid);seen.add(uid)
  print(f"  {w} (public={n}): {', '.join(ids[:6])}")
