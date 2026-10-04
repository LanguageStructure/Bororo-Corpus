#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confirm only archive witness correspondences that were manually reviewed.

This script does not infer matches. It checks that each reviewed witness still
points to the expected CorBo unit, then changes candidate -> confirmed.
"""
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"

CONFIRMED={
 "JAKO.073":"BOR-CORBO-HM001-u087",
 "JAKO.077":"BOR-CORBO-HM001-u091",
 "JAKO.078":"BOR-CORBO-HM001-u092",
 "JAKO.082":"BOR-CORBO-HM001-u096",
 "JAKO.083":"BOR-CORBO-HM001-u097",
 "JAKO.085":"BOR-CORBO-HM001-u099",
 "JAKO.087":"BOR-CORBO-HM001-u101",
 "JAKO.089":"BOR-CORBO-HM001-u103",
 "JAKO.090":"BOR-CORBO-HM001-u104",
 "JAKO.094":"BOR-CORBO-HM001-u108",
 "JAKO.095":"BOR-CORBO-HM001-u109",
 "JAKO.096":"BOR-CORBO-HM001-u110",
 "JAKO.097":"BOR-CORBO-HM001-u111",
 "JAKO.100":"BOR-CORBO-HM001-u114",
 "JAKO.101":"BOR-CORBO-HM001-u115",
 "JAKO.102":"BOR-CORBO-HM001-u116",
 "JAKO.103":"BOR-CORBO-HM001-u117",
 "JAKO.106":"BOR-CORBO-HM001-u120",
 "JAKO.107":"BOR-CORBO-HM001-u121",
 "JAKO.109":"BOR-CORBO-HM001-u123",
 "JAKO.110":"BOR-CORBO-HM001-u124",
 "JAKO.111":"BOR-CORBO-HM001-u125",
 "JAKO.113":"BOR-CORBO-HM001-u127",
 "JAKO.116":"BOR-CORBO-HM001-u130",
 "JAKO.117":"BOR-CORBO-HM001-u131",
 "JAKO.118":"BOR-CORBO-HM001-u132",
 "JAKO.119":"BOR-CORBO-HM001-u133",
 "JAKO.120":"BOR-CORBO-HM001-u134",
}

with W.open(encoding="utf-8",newline="") as f:
 rows=list(csv.DictReader(f,delimiter="\t"))

by_id={r["witness_id"]:r for r in rows}
missing=[wid for wid in CONFIRMED if wid not in by_id]
if missing:
 raise SystemExit("IDs ausentes: "+", ".join(missing))

errors=[]
for wid,target in CONFIRMED.items():
 r=by_id[wid]
 if r.get("corbo_match_id")!=target:
  errors.append(f"{wid}: esperado {target}, encontrado {r.get('corbo_match_id','') or '—'}")
 if r.get("collation_status") not in ("candidate","confirmed"):
  errors.append(f"{wid}: status inesperado {r.get('collation_status','') or '—'}")
if errors:
 raise SystemExit("Confirmação abortada:\n" + "\n".join(errors))

changed=0
for wid,target in CONFIRMED.items():
 r=by_id[wid]
 if r["collation_status"]!="confirmed":
  r["collation_status"]="confirmed"
  changed+=1

with W.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter="\t",lineterminator="\n")
 w.writeheader();w.writerows(rows)

print(f"Revisados explicitamente: {len(CONFIRMED)}")
print(f"Alterados para confirmed: {changed}")
for wid,target in CONFIRMED.items():
 print(f"{wid} -> {target} [confirmed]")
