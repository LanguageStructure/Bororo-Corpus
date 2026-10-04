#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confirm only archive witness correspondences that were manually reviewed.

This script does not infer matches. It checks that each reviewed witness still
points to the expected CorBo unit, then changes reviewed candidate/exact matches -> confirmed.
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

EXACT_REVIEWED={
 "JAKO.071":"BOR-CORBO-HM001-u085",
 "JAKO.072":"BOR-CORBO-HM001-u086",
 "JAKO.074":"BOR-CORBO-HM001-u088",
 "JAKO.075":"BOR-CORBO-HM001-u089",
 "JAKO.076":"BOR-CORBO-HM001-u090",
 "JAKO.079":"BOR-CORBO-HM001-u093",
 "JAKO.080":"BOR-CORBO-HM001-u094",
 "JAKO.081":"BOR-CORBO-HM001-u095",
 "JAKO.084":"BOR-CORBO-HM001-u098",
 "JAKO.086":"BOR-CORBO-HM001-u100",
 "JAKO.088":"BOR-CORBO-HM001-u102",
 "JAKO.091":"BOR-CORBO-HM001-u105",
 "JAKO.092":"BOR-CORBO-HM001-u106",
 "JAKO.093":"BOR-CORBO-HM001-u107",
 "JAKO.098":"BOR-CORBO-HM001-u112",
 "JAKO.099":"BOR-CORBO-HM001-u113",
 "JAKO.104":"BOR-CORBO-HM001-u118",
 "JAKO.105":"BOR-CORBO-HM001-u119",
 "JAKO.108":"BOR-CORBO-HM001-u122",
 "JAKO.112":"BOR-CORBO-HM001-u126",
 "JAKO.114":"BOR-CORBO-HM001-u128",
 "JAKO.115":"BOR-CORBO-HM001-u129",
 "JAKO.121":"BOR-CORBO-HM001-u135",
 "JAKO.122":"BOR-CORBO-HM001-u136",
}


with W.open(encoding="utf-8",newline="") as f:
 rows=list(csv.DictReader(f,delimiter="\t"))

by_id={r["witness_id"]:r for r in rows}
ALL_REVIEWED={**CONFIRMED,**EXACT_REVIEWED}
missing=[wid for wid in ALL_REVIEWED if wid not in by_id]
if missing:
 raise SystemExit("IDs ausentes: "+", ".join(missing))

errors=[]
for wid,target in ALL_REVIEWED.items():
 r=by_id[wid]
 if r.get("corbo_match_id")!=target:
  errors.append(f"{wid}: esperado {target}, encontrado {r.get('corbo_match_id','') or '—'}")
 expected=("exact","confirmed") if wid in EXACT_REVIEWED else ("candidate","confirmed")
 if r.get("collation_status") not in expected:
  errors.append(f"{wid}: status inesperado {r.get('collation_status','') or '—'}")
if errors:
 raise SystemExit("Confirmação abortada:\n" + "\n".join(errors))

changed=0
for wid,target in ALL_REVIEWED.items():
 r=by_id[wid]
 if r["collation_status"]!="confirmed":
  prior=r["collation_status"]
  r["collation_status"]="confirmed"
  if prior=="exact":
   note=r.get("editorial_note","")
   tag="Human-reviewed exact correspondence."
   if tag not in note:r["editorial_note"]=(note+" " if note else "")+tag
  changed+=1

with W.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter="\t",lineterminator="\n")
 w.writeheader();w.writerows(rows)

print(f"Revisados explicitamente: {len(ALL_REVIEWED)} ({len(CONFIRMED)} candidatos + {len(EXACT_REVIEWED)} exatos)")
print(f"Alterados para confirmed: {changed}")
for wid,target in ALL_REVIEWED.items():
 print(f"{wid} -> {target} [confirmed]")
