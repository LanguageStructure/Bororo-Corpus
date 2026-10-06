#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct comparison of name-anchored JAKO units with HM candidates."""
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
pairs={"JAKO.061":["BOR-CORBO-HM001-u133"],"JAKO.065":["BOR-CORBO-HM001-u107"],
"JAKO.067":["BOR-CORBO-HM001-u109"],"JAKO.069":["BOR-CORBO-HM001-u111"],
"JAKO.070":["BOR-CORBO-HM001-u112","BOR-CORBO-HM001-u038"]}
with W.open(encoding="utf-8",newline="") as f: wr={r["witness_id"]:r for r in csv.DictReader(f,delimiter="\t")}
raw=json.loads(P.read_text(encoding="utf-8"));units=raw if isinstance(raw,list) else raw.get("units",[])
pu={str(u.get("id","")):u for u in units}
for wid,ids in pairs.items():
 r=wr[wid]
 print(f"\n=== {wid} ===")
 print("J-BOR:",r["source"].replace("\n"," "))
 print("J-POR:",r["portuguese"].replace("\n"," "))
 for uid in ids:
  u=pu[uid]
  print(f"\n[{uid}]")
  print("H-BOR:",str(u.get("b") or u.get("source") or "").replace("\n"," "))
  print("H-POR:",str(u.get("p") or "").replace("\n"," "))
