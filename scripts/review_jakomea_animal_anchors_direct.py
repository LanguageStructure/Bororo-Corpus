#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct semantic review of discriminant animal anchors in JAKO.017-053."""
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
pairs={
"JAKO.020":["BOR-CORBO-COQ-S34-p021"],
"JAKO.026":["BOR-CORBO-COQ-S34-p046"],
"JAKO.037":["BOR-CORBO-COQ-S25-p017"],
"JAKO.044":["GBAK.027"],
"JAKO.049":["GBAK.028"],
"JAKO.052":["PAND.010","BOR-CORBO-COQ-S23-p033","AIJ.003"],
}
with W.open(encoding="utf-8",newline="") as f: wr={r["witness_id"]:r for r in csv.DictReader(f,delimiter="\t")}
raw=json.loads(P.read_text(encoding="utf-8"));units=raw if isinstance(raw,list) else raw.get("units",[])
pu={str(u.get("id","")):u for u in units}
for wid,ids in pairs.items():
 r=wr[wid]
 print(f"\n=== {wid} ===")
 print("J-BOR:",r["source"].replace("\n"," "))
 print("J-POR:",r["portuguese"].replace("\n"," "))
 for uid in ids:
  u=pu.get(uid)
  if not u: print(f"\n[{uid}] NÃO ENCONTRADA");continue
  print(f"\n[{uid}]")
  print("P-BOR:",str(u.get("b") or u.get("source") or "").replace("\n"," "))
  print("P-POR:",str(u.get("p") or "").replace("\n"," "))
