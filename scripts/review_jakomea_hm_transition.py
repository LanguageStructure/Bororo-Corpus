#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print the JAKO/HM transition around the first confirmed JAKO anchor."""
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
with W.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
print("=== JAKOMEA JIWU: JAKO.066–076 ===")
for r in rows:
 m=re.fullmatch(r"JAKO\.(\d+)",r["witness_id"])
 if m and 66<=int(m.group(1))<=76:
  print(f"\n[{r['witness_id']}] status={r.get('collation_status','')} match={r.get('corbo_match_id','')}")
  print("BOR:",r.get("source","").replace("\n"," "))
  print("POR:",r.get("portuguese","").replace("\n"," "))
raw=json.loads(P.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
print("\n=== HISTÓRIA MÍTICA: u080–u090 ===")
for u in units:
 m=re.fullmatch(r"BOR-CORBO-HM001-u(\d+)",str(u.get("id","")))
 if m and 80<=int(m.group(1))<=90:
  print(f"\n[{u.get('id')}]")
  print("BOR:",str(u.get("b") or u.get("source") or "").replace("\n"," "))
  print("POR:",str(u.get("p") or "").replace("\n"," "))
