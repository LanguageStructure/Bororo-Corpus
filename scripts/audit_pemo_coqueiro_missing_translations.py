#!/usr/bin/env python3
"""Inspect untranslated Pemo-Coqueiro staging units in local context. No writes."""
from pathlib import Path
import csv

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"

with P.open(encoding="utf-8",newline="") as f:
 rows=list(csv.DictReader(f,delimiter="\t"))

missing=[i for i,r in enumerate(rows) if not (r.get("portuguese") or "").strip()]
print(f"Pemo-Coqueiro: {len(missing)} unidades sem tradução\n")
for i in missing:
 r=rows[i]
 print("="*90)
 print(f"{r['id']} | número-fonte={r.get('source_number','')} | seção={r.get('section','')}")
 print("BORORO:",(r.get("source") or "").replace("\\n"," "))
 print("REVIEWED:",(r.get("reviewed") or "").replace("\\n"," "))
 print("NOTA:",(r.get("editorial_note") or "").replace("\\n"," "))
 for j,label in ((i-1,"ANTERIOR"),(i+1,"SEGUINTE")):
  if 0<=j<len(rows):
   x=rows[j]
   print(f"{label}: {x['id']} | número-fonte={x.get('source_number','')}")
   print("  BOR:",(x.get("source") or "").replace("\\n"," "))
   print("  PT :", (x.get("portuguese") or "").replace("\\n"," "))
 print()
