#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find monotonic Pemo-Coqueiro / Historia Mitica runs among prefix candidates.

Consumes /tmp/pc_prefix.txt. A run requires increasing PC IDs and increasing HM IDs
with bounded gaps; it is a review aid, not an automatic matcher.
"""
from pathlib import Path
import re
P=Path("/tmp/pc_prefix.txt")
if not P.exists(): raise SystemExit("Gere /tmp/pc_prefix.txt primeiro.")
t=P.read_text(encoding="utf-8")
pat=re.compile(r"^(PC\.(\d+)) => (BOR-CORBO-HM001-u(\d+)) \| score=([0-9.]+); texto=([0-9.]+); lexical=([0-9.]+); coleção=História Mítica$",re.M)
a=[(int(pn),int(hn),pc,hm,float(sc),float(tx),float(lx)) for pc,pn,hm,hn,sc,tx,lx in pat.findall(t)]
a.sort()
print("PEMO–COQUEIRO — RUNS MONOTÔNICOS HM")
print(f"candidatos HM de entrada: {len(a)}")
print("Critério: PC e HM crescem; ΔPC <= 5; ΔHM <= 5. Diagnóstico somente.\n")
runs=[]
for i,x in enumerate(a):
 run=[x]; last=x
 for y in a[i+1:]:
  dp=y[0]-last[0]; dh=y[1]-last[1]
  if dp<=0: continue
  if dp<=5 and 0<dh<=5:
   run.append(y); last=y
  elif dp>5: break
 if len(run)>=2:runs.append(run)
# remove runs that are strict subsets
uniq=[]
sets=[]
for r in sorted(runs,key=lambda r:(-len(r),r[0][0])):
 s={(x[0],x[1]) for x in r}
 if any(s < q for q in sets):continue
 uniq.append(r);sets.append(s)
for k,r in enumerate(sorted(uniq,key=lambda r:r[0][0]),1):
 print(f"RUN {k}: {len(r)} âncoras")
 for x in r:
  print(f"  {x[2]} => {x[3]} | score={x[4]:.3f}; texto={x[5]:.3f}; lexical={x[6]:.3f}")
 print()
print("PARES CONSECUTIVOS EXATOS DE POSIÇÃO (ΔPC=ΔHM=1)")
for x,y in zip(a,a[1:]):
 if y[0]-x[0]==1 and y[1]-x[1]==1:
  print(f"  {x[2]}→{x[3]} ; {y[2]}→{y[3]}")
