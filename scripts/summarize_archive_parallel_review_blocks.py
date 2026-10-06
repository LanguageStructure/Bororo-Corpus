#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summarize archive parallel witnesses around existing human anchors.

Shows per-document counts and contiguous unmatched spans bounded by confirmed/
component decisions. This defines the blocks for conservative contextual review.
"""
from __future__ import annotations
import csv
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
docs=defaultdict(list)
for r in rows:docs[r["document"]].append(r)
for doc,rs in docs.items():
 c=Counter((r.get("collation_status") or "").strip() for r in rs)
 print(f"\n### {doc} ({len(rs)})")
 print("status:",", ".join(f"{k or '<empty>'}={v}" for k,v in sorted(c.items())))
 start=None
 for i,r in enumerate(rs):
  st=(r.get("collation_status") or "").strip()
  if st=="unmatched" and start is None:start=i
  end=(st!="unmatched" and start is not None)
  if end:
   block=rs[start:i]
   left=rs[start-1] if start else None
   right=r
   print(f"UNMATCHED {block[0]['witness_id']}..{block[-1]['witness_id']} ({len(block)})")
   if left:print(f"  left: {left['witness_id']} {left.get('collation_status','')} -> {left.get('corbo_match_id','')}")
   print(f"  right: {right['witness_id']} {right.get('collation_status','')} -> {right.get('corbo_match_id','')}")
   start=None
 if start is not None:
  block=rs[start:]
  left=rs[start-1] if start else None
  print(f"UNMATCHED {block[0]['witness_id']}..{block[-1]['witness_id']} ({len(block)})")
  if left:print(f"  left: {left['witness_id']} {left.get('collation_status','')} -> {left.get('corbo_match_id','')}")
  print("  right: <end>")
