#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Review JAKO.054-070 against all História Mítica, emphasizing rare/name anchors."""
from __future__ import annotations
import csv,json,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s);return " ".join(s.split())
with W.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
j=[r for r in rows if (m:=re.fullmatch(r"JAKO\.(\d+)",r["witness_id"])) and 54<=int(m.group(1))<=70]
raw=json.loads(P.read_text(encoding="utf-8"));units=raw if isinstance(raw,list) else raw.get("units",[])
hm=[u for u in units if str(u.get("id","")).startswith("BOR-CORBO-HM001-u")]
for r in j:
 a=norm(r["source"]);ap=norm(r.get("portuguese",""))
 scored=[]
 for u in hm:
  b=norm(u.get("b") or u.get("source") or "");bp=norm(u.get("p") or "")
  sb=SequenceMatcher(None,a,b,autojunk=True).ratio()
  sp=SequenceMatcher(None,ap,bp,autojunk=True).ratio() if ap and bp else 0
  # Portuguese semantics and Bororo jointly; names naturally boost both.
  score=.65*sb+.35*sp
  scored.append((score,sb,sp,u))
 print(f"\n=== {r['witness_id']} ===")
 print("J-POR:",r.get("portuguese","").replace("\n"," "))
 for score,sb,sp,u in sorted(scored,reverse=True,key=lambda x:x[0])[:3]:
  print(f"{u.get('id')} combined={score:.3f} bor={sb:.3f} por={sp:.3f}")
  print("H-POR:",str(u.get("p") or "").replace("\n"," "))
