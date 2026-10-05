#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnose the pre-anchor Pemo-Coqueiro block (PC < 276) against the public corpus.

Uses lexical fingerprints to find plausible public collections/units without promoting
matches. Exact/near-exact matches remain authoritative elsewhere; this report is for
structural discovery only.
"""
from __future__ import annotations
import csv,json,re,unicodedata,collections
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PC=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"
PUB=ROOT/"docs/data/corbo-units.json"
STOP={"icare","ure","akore","egore","dukeje","pugeje","nowu","boe","eie","reo","ji","to","ei","du","mare","oino","ca","ere","ema","karega"}
def norm(s):
 s=unicodedata.normalize("NFC",str(s or "")).casefold()
 s=re.sub(r"[^a-záéíóúâêôãõçüñ]+"," ",s);return " ".join(s.split())
def toks(s):return [x for x in norm(s).split() if len(x)>=4 and x not in STOP]
def rows(p):
 with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def n(x):
 m=re.search(r"(\d+)$",x or "");return int(m.group(1)) if m else 999999
data=json.loads(PUB.read_text(encoding="utf-8")); units=data if isinstance(data,list) else data.get("units",[])
P=rows(PC); P=[r for r in P if n(r["id"])<276]
docs=[]
df=collections.Counter()
for u in units:
 text=str(u.get("b") or u.get("source") or ""); ts=set(toks(text))
 if not ts:continue
 docs.append((u,text,ts))
 df.update(ts)
N=max(1,len(docs))
def coll(u):
 return str(u.get("collection") or u.get("source_collection") or u.get("document") or u.get("source") or "unknown")
print("PEMO–COQUEIRO PC.001–275 — DIAGNÓSTICO ESTRUTURAL CONTRA CORPUS PÚBLICO")
print(f"unidades staging analisadas: {len(P)}; unidades públicas indexadas: {len(docs)}")
print("Resultados abaixo são candidatos estruturais, nunca correspondências automáticas.\n")
counts=collections.Counter(); strong=[]
for r in P:
 src=r.get("reviewed") or r.get("source") or ""; st=set(toks(src))
 # rare-token weighted overlap, then SequenceMatcher on top shortlist
 cand=[]
 for u,text,ut in docs:
  inter=st & ut
  if not inter:continue
  weight=sum(1.0/(1+df[t]) for t in inter)
  coverage=len(inter)/max(1,len(st))
  cand.append((weight+coverage,u,text,inter))
 cand.sort(key=lambda x:x[0],reverse=True)
 best=[]
 for _,u,text,inter in cand[:30]:
  s=SequenceMatcher(None,norm(src),norm(text),autojunk=False).ratio()
  lex=len(inter)/max(1,len(st|set(toks(text))))
  score=max(s,lex)
  best.append((score,s,lex,u,text,inter))
 if not best:continue
 best.sort(key=lambda x:x[0],reverse=True); b=best[0]
 counts[coll(b[3])]+=1
 if b[0]>=.55:
  strong.append((r,b))
print("Melhor destino por unidade (contagem diagnóstica):")
for k,v in counts.most_common(15):print(f"  {k}: {v}")
print(f"\nCandidatos estruturais com score >=0.55: {len(strong)}")
for r,b in strong[:80]:
 score,s,lex,u,text,inter=b
 print("\n"+"="*96)
 print(f"{r['id']} => {u.get('id','?')} | score={score:.3f}; texto={s:.3f}; lexical={lex:.3f}; coleção={coll(u)}")
 print("âncoras:",", ".join(sorted(inter)[:16]))
 print("PC:",(r.get("reviewed") or r.get("source") or "").replace("\n"," "))
 print("PUB:",text.replace("\n"," "))
