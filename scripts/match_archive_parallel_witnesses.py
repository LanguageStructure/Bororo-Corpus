#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Conservative matching of staged archive witnesses against Historia Mitica collation."""
import csv,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
C=ROOT/"CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv"

def norm(s):
 s=unicodedata.normalize("NFC",s or "").lower()
 s=s.replace("\\n"," ")
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())

with W.open(encoding="utf-8") as f: wr=list(csv.DictReader(f,delimiter="\t"))
with C.open(encoding="utf-8") as f: cr=list(csv.DictReader(f,delimiter="\t"))
targets=[]
for r in cr:
 for field in ("witness_a","witness_b","reviewed"):
  n=norm(r.get(field,""))
  if n: targets.append((n,r["id"],field))
exact={}
for n,i,field in targets: exact.setdefault(n,[]).append((i,field))
counts={"exact":0,"candidate":0,"unmatched":0}
for r in wr:
 n=norm(r["source"])
 if n in exact:
  hits=exact[n]
  ids=sorted(set(i for i,_ in hits))
  r["collation_status"]="exact"
  r["corbo_match_id"]=";".join(ids)
  r["editorial_note"]=(r["editorial_note"]+" " if r["editorial_note"] else "")+"Exact normalized Bororo match."
  counts["exact"]+=1
  continue
 best=(0.0,None,None)
 if n:
  # Cheap length filter prevents unrelated long/short comparisons.
  for t,i,field in targets:
   ratio=len(n)/len(t)
   if ratio<0.65 or ratio>1.55: continue
   score=SequenceMatcher(None,n,t,autojunk=False).ratio()
   if score>best[0]: best=(score,i,field)
 # In highly formulaic passages, ~0.90 can match the wrong named participant.
 # Require near-identity for automatic candidate surfacing; lower scores remain
 # unmatched for later structure/name-aware collation.
 if best[0]>=0.99:
  r["collation_status"]="candidate"
  r["corbo_match_id"]=best[1]
  r["editorial_note"]=(r["editorial_note"]+" " if r["editorial_note"] else "")+f"High-similarity candidate ({best[0]:.3f}); requires human confirmation."
  counts["candidate"]+=1
 else:
  r["collation_status"]="unmatched"; r["corbo_match_id"]=""
  counts["unmatched"]+=1
with W.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=wr[0].keys(),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(wr)
print("Matching concluído:",counts)
print("Somente exact é correspondência automática; candidate (>=0.99) exige revisão humana.")
