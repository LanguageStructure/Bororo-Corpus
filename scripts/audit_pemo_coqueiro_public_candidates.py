#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit non-equivalent Pemo-Coqueiro units against the whole public CorBo.

Read-only. Collation 'confirmed' units are excluded because they are already
represented by their documented HM correspondence. The remaining unique and
parallel_formulaic units are checked against every public unit for exact and
near-exact Bororo duplication.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
PC=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"
COL=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_collation.tsv"
PUB=ROOT/"docs/data/corbo-units.json"

def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())

def score(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0.0

with PC.open(encoding="utf-8",newline="") as f:
 pc={r["id"]:r for r in csv.DictReader(f,delimiter="\t")}
with COL.open(encoding="utf-8",newline="") as f:
 col=list(csv.DictReader(f,delimiter="\t"))
raw=json.loads(PUB.read_text(encoding="utf-8"))
units=raw if isinstance(raw,list) else raw.get("units",[])

public=[]
for u in units:
 text=u.get("b") or u.get("source") or u.get("text") or ""
 if norm(text):
  public.append((str(u.get("id","")),str(u.get("document") or u.get("title") or u.get("source_file") or ""),text))

candidates=[r for r in col if r["status"] in {"unique","parallel_formulaic"}]
counts=Counter()
strong=[]
for d in candidates:
 r=pc[d["id"]]
 src=r.get("reviewed") or r.get("source") or ""
 ns=norm(src)
 exact=[u for u in public if norm(u[2])==ns]
 if exact:
  counts["exact"]+=1
  strong.append((d["id"],d["status"],1.0,exact[0]))
  continue
 best=max(((score(src,u[2]),u) for u in public),default=(0.0,("","","")),key=lambda z:z[0])
 if best[0]>=0.99:
  counts["near_exact"]+=1
  strong.append((d["id"],d["status"],best[0],best[1]))
 else:
  counts["no_strong_duplicate"]+=1

print(f"Candidatos não equivalentes auditados: {len(candidates)}")
print(f"exact: {counts['exact']}")
print(f"near_exact >=0.99: {counts['near_exact']}")
print(f"sem duplicata forte: {counts['no_strong_duplicate']}")
print("\nCORRESPONDÊNCIAS FORTES (exigem revisão antes de excluir)")
for pid,status,s,(uid,doc,text) in strong:
 print(f"{pid}\t{status}\t{s:.3f}\t{uid}\t{doc}\t{text}")
