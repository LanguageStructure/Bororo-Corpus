#!/usr/bin/env python3
"""Audit editorial staging TSVs without modifying them."""
from pathlib import Path
import csv
from collections import Counter, defaultdict

ROOT=Path(__file__).resolve().parents[1]
FILES=[
 ("Pemo — Baraedugume",ROOT/"CorBo_vNext/texts/pemo-baraedugume/pemo_baraedugume_editorial.tsv"),
 ("Pemo — Coqueiro",ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"),
 ("Arquivo — novos testemunhos",ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"),
]

def clean(s): return (s or "").strip()

total=Counter()
print("AUDITORIA DA CAMADA DOCUMENTAL EM STAGING\n")
for label,path in FILES:
 with path.open(encoding="utf-8",newline="") as f:
  rows=list(csv.DictReader(f,delimiter="\t"))
 ids=Counter(clean(r.get("id")) for r in rows)
 dup=[k for k,v in ids.items() if k and v>1]
 source_empty=[r for r in rows if not clean(r.get("source"))]
 pt_empty=[r for r in rows if not clean(r.get("portuguese"))]
 reviewed=[r for r in rows if clean(r.get("reviewed"))]
 changed=[r for r in reviewed if clean(r.get("reviewed"))!=clean(r.get("source"))]
 unchanged=[r for r in reviewed if clean(r.get("reviewed"))==clean(r.get("source"))]
 notes=[r for r in rows if clean(r.get("editorial_note"))]
 print(f"{label}: {len(rows)}")
 print(f"  reviewed preenchido: {len(reviewed)} (alterado: {len(changed)}; igual à fonte: {len(unchanged)})")
 print(f"  tradução ausente: {len(pt_empty)}")
 print(f"  fonte vazia: {len(source_empty)}")
 print(f"  notas editoriais: {len(notes)}")
 print(f"  IDs duplicados: {len(dup)}")
 if pt_empty: print("  IDs sem tradução:",", ".join(clean(r.get("id")) for r in pt_empty[:30]))
 if source_empty: print("  IDs sem fonte:",", ".join(clean(r.get("id")) for r in source_empty[:30]))
 if dup: print("  IDs duplicados:",", ".join(dup[:30]))
 if "document" in (rows[0] if rows else {}):
  bydoc=defaultdict(lambda:Counter())
  for r in rows:
   d=clean(r.get("document")) or "(sem documento)"
   bydoc[d]["total"]+=1
   if clean(r.get("reviewed")): bydoc[d]["reviewed"]+=1
   if not clean(r.get("portuguese")): bydoc[d]["no_pt"]+=1
  print("  por documento:")
  for d,x in sorted(bydoc.items()):
   print(f"    {d}: {x['total']} | reviewed={x['reviewed']} | sem_pt={x['no_pt']}")
 print()
 total["rows"]+=len(rows); total["reviewed"]+=len(reviewed); total["changed"]+=len(changed)
 total["no_pt"]+=len(pt_empty); total["source_empty"]+=len(source_empty); total["dup"]+=len(dup)

print("TOTAL")
print(f"  unidades: {total['rows']}")
print(f"  reviewed preenchido: {total['reviewed']} (alterado: {total['changed']})")
print(f"  tradução ausente: {total['no_pt']}")
print(f"  fonte vazia: {total['source_empty']}")
print(f"  IDs duplicados: {total['dup']}")
