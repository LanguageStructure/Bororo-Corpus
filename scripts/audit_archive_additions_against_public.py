#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit archive-additions against the complete current public CorBo.

Read-only. Reports exact and near-exact Bororo matches; no match is promoted
or excluded automatically.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
PUB=ROOT/"docs/data/corbo-units.json"

def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())

def sim(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0.0

with SRC.open(encoding="utf-8",newline="") as f:
 rows=list(csv.DictReader(f,delimiter="\t"))
raw=json.loads(PUB.read_text(encoding="utf-8"))
units=raw if isinstance(raw,list) else raw.get("units",[])
public=[]
for u in units:
 text=u.get("b") or u.get("source") or u.get("text") or ""
 if norm(text):
  public.append((str(u.get("id","")),str(u.get("collection") or u.get("document") or u.get("title") or ""),text))

counts=Counter(); strong=[]
for r in rows:
 src=(r.get("reviewed") or r.get("source") or "").strip()
 ns=norm(src)
 exact=[u for u in public if norm(u[2])==ns]
 if exact:
  counts["exact"]+=1;strong.append((r["id"],r["document"],1.0,exact[0]));continue
 best=max(((sim(src,u[2]),u) for u in public),default=(0.0,("","","")),key=lambda z:z[0])
 if best[0]>=.99:
  counts["near_exact"]+=1;strong.append((r["id"],r["document"],best[0],best[1]))
 else:counts["no_strong_duplicate"]+=1

print(f"Archive-additions auditadas: {len(rows)}")
print(f"exact: {counts['exact']}")
print(f"near_exact >=0.99: {counts['near_exact']}")
print(f"sem duplicata forte: {counts['no_strong_duplicate']}")
print("\nCORRESPONDÊNCIAS FORTES (revisão humana antes de excluir)")
for aid,doc,s,(uid,collection,text) in strong:
 print(f"{aid}\t{doc}\t{s:.3f}\t{uid}\t{collection}\t{text}")
