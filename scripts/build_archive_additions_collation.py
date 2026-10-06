#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build persistent publication decisions for archive-additions.

The completed public-corpus audit found no documentary duplicate among the
226 units. This layer records that result separately from source/review text.
"""
from __future__ import annotations
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
OUT=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_collation.tsv"
with SRC.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
with OUT.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=["id","status","corbo_match_id","decision_note"],delimiter="\t",lineterminator="\n")
 w.writeheader()
 for r in rows:
  w.writerow({"id":r["id"],"status":"unique","corbo_match_id":"","decision_note":"No documentary duplicate identified in completed public-corpus audit."})
print(f"Unidades: {len(rows)}")
print("unique:",len(rows))
print("confirmed: 0")
print("parallel_formulaic: 0")
print("unresolved: 0")
