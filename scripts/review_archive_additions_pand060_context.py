#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused context for the only sequence candidates in archive-additions."""
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
P=ROOT/"docs/data/corbo-units.json"
with A.open(encoding="utf-8",newline="") as f: ar=list(csv.DictReader(f,delimiter="\t"))
raw=json.loads(P.read_text(encoding="utf-8")); pu=raw if isinstance(raw,list) else raw.get("units",[])
am={r["id"]:r for r in ar}; pm={str(r.get("id","")):r for r in pu}
def showa(uid):
 r=am.get(uid)
 if not r:return
 print("\n",uid,r.get("document",""))
 print("BOR:",(r.get("reviewed") or r.get("source") or "").replace("\n"," "))
 print("POR:",(r.get("portuguese") or "").replace("\n"," "))
def showp(uid):
 r=pm.get(uid)
 if not r:return
 print("\n",uid,r.get("collection",""))
 print("BOR:",str(r.get("b") or r.get("source") or "").replace("\n"," "))
 print("POR:",str(r.get("p") or "").replace("\n"," "))
print("=== PRIMEIRAS ANDANÇAS ===")
for n in range(58,65):showa(f"PAND.{n:03d}")
print("\n=== COQUEIRO ===")
for n in range(28,34):showp(f"BOR-CORBO-COQ-S08-p{n:03d}")
print("\n=== PEMO-COQUEIRO ===")
for n in range(268,277):showp(f"PC.{n:03d}")
