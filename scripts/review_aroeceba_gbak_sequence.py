#!/usr/bin/env python3
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
ARC=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
def read(path):
 with path.open(encoding="utf-8") as f: return list(csv.DictReader(f,delimiter="\t"))
w=read(W); a=read(ARC)
ar={r["witness_id"]:r for r in w if r["witness_id"].startswith("AROC.")}
gb={r["id"]:r for r in a if r["id"].startswith("GBAK.")}
for i in range(14,33):
 aid=f"AROC.{i:03d}"
 r=ar.get(aid)
 if not r: continue
 print("\n"+"="*72)
 print(aid)
 print("A-BOR:",r.get("source","").replace("\\n"," "))
 print("A-POR:",r.get("portuguese","").replace("\\n"," "))
 # expected neighborhood suggested by AROC.016->GBAK.035
 center=35+(i-16)
 lo=max(1,center-2); hi=center+2
 for j in range(lo,hi+1):
  gid=f"GBAK.{j:03d}"; g=gb.get(gid)
  if not g: continue
  print(f"\n[{gid}]")
  print("G-BOR:",g.get("reviewed") or g.get("source",""))
  print("G-POR:",g.get("portuguese",""))
