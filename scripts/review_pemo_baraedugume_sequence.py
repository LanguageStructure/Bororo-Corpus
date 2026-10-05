#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sequence-aware review of Pemo-Baraedugume against Historia Mitica.

Diagnostic only. Exact/near-exact anchors establish the expected PB.xxx -> HM001-uXXX
sequence, but unmatched rows are never promoted automatically.
"""
from __future__ import annotations
import csv,re,unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PB=ROOT/"CorBo_vNext/texts/pemo-baraedugume/pemo_baraedugume_editorial.tsv"
HM=ROOT/"CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv"

def tsv(p):
 with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold().replace("\\n"," ")
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s)
 return " ".join(s.split())
def sim(a,b):
 a,b=norm(a),norm(b)
 return SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0.0
def num(s):
 m=re.search(r"(\d+)$",s or "")
 return int(m.group(1)) if m else None

pb=tsv(PB);hm=tsv(HM)
by_u={num(r.get("id")):r for r in hm if num(r.get("id")) is not None}

def best_variant(src,r):
 vals=[]
 for f in ("reviewed","witness_a","witness_b"):
  v=(r.get(f) or "").strip()
  if v:vals.append((sim(src,v),f,v))
 return max(vals,key=lambda x:x[0]) if vals else (0.0,"","")

exact=near=0;unmatched=[]
for r in pb:
 n=num(r.get("id"));target=by_u.get(n)
 if not target:
  unmatched.append((r,None,0.0,"",""));continue
 score,field,text=best_variant((r.get("reviewed") or r.get("source") or ""),target)
 if score==1.0:exact+=1
 elif score>=0.99:near+=1
 else:unmatched.append((r,target,score,field,text))

print("PEMO–BARAEDUGUME × HISTÓRIA MÍTICA — REVISÃO POR SEQUÊNCIA")
print(f"mesmo número: exact={exact}; >=0.99={near}; abaixo de 0.99={len(unmatched)}")
print("Nenhuma decisão é gravada. Nomes, participantes, ação e tradução prevalecem sobre similaridade.\n")
for r,target,score,field,text in unmatched:
 n=num(r.get("id"))
 print("="*100)
 print(f"{r.get('id')} => esperado BOR-CORBO-HM001-u{n:03d} | sim={score:.3f} | variante={field or '-'}")
 print("PB BOR :", (r.get("reviewed") or r.get("source") or "").replace("\n"," "))
 print("PB PT  :", (r.get("portuguese") or "").replace("\n"," "))
 if target:
  print("HM BOR :", text.replace("\n"," "))
  print("HM PT  :", (target.get("portuguese") or "").replace("\n"," "))
  for d in (-1,1):
   q=by_u.get(n+d)
   if q:
    s,f,v=best_variant((r.get("reviewed") or r.get("source") or ""),q)
    print(f"VIZ {n+d:03d}: sim={s:.3f} | {v.replace(chr(10),' ')[:260]}")
 print()
