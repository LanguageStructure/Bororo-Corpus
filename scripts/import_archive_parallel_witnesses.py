#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage parallel Bororo archive witnesses for collation without adding them to public corpus counts."""
from __future__ import annotations
import csv,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
SPECS=[
 ("facanhaBakororogode.txt","FAC","Façanha Bakororogode"),
 ("bakororodoge.txt","BAKD","Bakororodoge"),
 ("aroeeceba.txt","AROC","Aroeceba"),
 ("aruaBororo.txt","ARUA","Arua Bororo"),
 ("aruaBororoII.txt","ARU2","Arua Bororo II"),
 ("ipareEwororo.txt","IPEW","Ipare Ewororo"),
 ("jakomeaJiwu.txt","JAKO","Jakomea Jiwu"),
 ("ciriloDiscurso.txt","CIR","Cirilo Discurso"),
]
FIELDS=["witness_id","document","source_file","source_number","section","source","portuguese","collation_status","corbo_match_id","editorial_note"]

def numbered(s):
 m=re.match(r"^\s*(\d{1,3})\s*[.)]?\s*(.*\S)?\s*$",s)
 return (m.group(1),(m.group(2) or "").strip()) if m else None

def numbered_heading(s):
 m=re.match(r"^\s*\d{1,3}\s*[.)]\s*(.+?)\s*$",s)
 if not m:return False
 b=m.group(1)
 return bool(len(b)<180 and any(c.isalpha() for c in b) and b.upper()==b)

def heading(s):
 return bool(s and not numbered(s) and len(s)<180 and any(c.isalpha() for c in s)
             and s.upper()==s)

def parse(path,key,title):
 lines=path.read_text(encoding="utf-8-sig").replace("\r\n","\n").replace("\r","\n").splitlines()
 rows=[]; section=""; i=0
 while i<len(lines):
  s=lines[i].strip()
  if not s:i+=1;continue
  if numbered_heading(s) or heading(s):
   section=s;i+=1;continue
  a=numbered(s)
  if not a:i+=1;continue
  n,bor=a;i+=1
  bor_lines=[bor] if bor else []; por_lines=[];j=i;paired=False
  while j<len(lines):
   t=lines[j].strip()
   if not t:j+=1;continue
   if numbered_heading(t) or heading(t):break
   b=numbered(t)
   if b:
    if b[0]==n:
     por_lines=[b[1]] if b[1] else [];j+=1;paired=True
     while j<len(lines):
      u=lines[j].strip()
      if not u:j+=1;continue
      if numbered_heading(u) or heading(u) or numbered(u):break
      por_lines.append(u);j+=1
     i=j
    break
   bor_lines.append(t);j+=1
  if not paired:i=j
  rows.append({
   "witness_id":f"{key}.{len(rows)+1:03d}","document":title,"source_file":path.name,
   "source_number":n,"section":section,"source":"\\n".join(bor_lines).strip(),
   "portuguese":"\\n".join(por_lines).strip(),"collation_status":"unmatched",
   "corbo_match_id":"","editorial_note":""
  })
 return rows

def main():
 if len(sys.argv)!=2:
  raise SystemExit("Uso: python3 scripts/import_archive_parallel_witnesses.py '/caminho/Bororo Corpus'")
 base=Path(sys.argv[1]).expanduser().resolve()
 allrows=[]
 for fn,key,title in SPECS:
  p=base/fn
  if not p.exists():raise SystemExit(f"Arquivo obrigatório não encontrado: {p}")
  rs=parse(p,key,title)
  print(f"{fn}: {len(rs)} unidades documentais")
  allrows.extend(rs)
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t",lineterminator="\n")
  w.writeheader();w.writerows(allrows)
 print(f"OK: {len(allrows)} unidades testemunhais -> {OUT.relative_to(ROOT)}")
 print("Nenhuma unidade é incorporada ao corpus público; collation_status começa como unmatched.")

if __name__=="__main__":main()
