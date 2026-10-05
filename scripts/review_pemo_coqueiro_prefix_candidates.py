#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused review of structural candidates for PC.001-275.

Prints candidates >=.55 grouped by destination collection and highlights local
PC runs that repeatedly point to the same public collection/unit neighborhood.
Diagnostic only; writes nothing.
"""
from __future__ import annotations
import re
from pathlib import Path
SRC=Path("/tmp/pc_prefix.txt")
if not SRC.exists():
 raise SystemExit("Execute primeiro: python3 scripts/diagnose_pemo_coqueiro_prefix.py > /tmp/pc_prefix.txt")
text=SRC.read_text(encoding="utf-8")
blocks=re.split(r"={20,}\n",text)
items=[]
pat=re.compile(r"^(PC\.\d+) => (\S+) \| score=([0-9.]+); texto=([0-9.]+); lexical=([0-9.]+); coleção=(.+)$",re.M)
for b in blocks:
 m=pat.search(b)
 if m:
  pc,target,score,ts,lex,coll=m.groups()
  items.append((int(pc.split(".")[1]),pc,target,float(score),float(ts),float(lex),coll.strip(),b.strip()))
print("PC.001–275 — REVISÃO FOCADA DOS CANDIDATOS >=0.55")
print(f"candidatos: {len(items)}\n")
from collections import Counter,defaultdict
by=defaultdict(list)
for x in items:by[x[6]].append(x)
for coll,vals in sorted(by.items(),key=lambda kv:(-len(kv[1]),kv[0])):
 print(f"## {coll}: {len(vals)}")
 for x in vals:
  print(f"{x[1]} => {x[2]} | score={x[3]:.3f}; texto={x[4]:.3f}; lexical={x[5]:.3f}")
 print()
print("## RUNS LOCAIS")
s=sorted(items)
for i,x in enumerate(s):
 neigh=[y for y in s if abs(y[0]-x[0])<=3 and y[6]==x[6]]
 if len(neigh)>=2:
  ids=", ".join(f"{y[1]}→{y[2]}" for y in neigh)
  print(f"{x[6]} | {ids}")
print("\n## DETALHES — História Mítica / Coqueiro")
for x in s:
 if x[6] in {"História Mítica","Coqueiro"}:
  print("\n"+"="*96);print(x[7])
