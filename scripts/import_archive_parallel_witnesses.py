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
 # Repairs for documentary layouts verified against the source files.
 if path.name=="facanhaBakororogode.txt":
  for r in rows:
   marker="\\nEntão o pai deles fez."
   if r["source_number"]=="3" and not r["portuguese"] and marker in r["source"]:
    r["source"],tail=r["source"].split(marker,1)
    r["portuguese"]="Então o pai deles fez."+tail
    r["editorial_note"]="Portuguese translation follows Bororo without a repeated number."
  rows=[r for r in rows if "O PAI FABRICA-LHES" not in r["source"]]
 if path.name=="bakororodoge.txt":
  for i in range(len(rows)-1):
   if rows[i]["source_number"]=="44" and rows[i+1]["source_number"]=="44" and not rows[i]["portuguese"]:
    rows[i]["portuguese"]=rows[i+1]["source"]; rows[i]["editorial_note"]="Portuguese translation is printed as a second unit 44."; rows.pop(i+1); break
  idx=[i for i,r in enumerate(rows) if "CANTO SOBRE OS BAKORORODOGE" in r["section"]]
  if len(idx)>=8:
   block=[rows[i] for i in idx]
   if [r["source_number"] for r in block[:8]]==["51","1","2","3","51","1","2","3"]:
    for a,b in zip(block[:4],block[4:8]):
     a["portuguese"]=b["source"]; a["editorial_note"]="Portuguese translation occurs in the second numbered sequence of the song."
    drop_ids={id(r) for r in block[4:8]}; rows=[r for r in rows if id(r) not in drop_ids]
 if path.name=="ipareEwororo.txt":
  rows=[r for r in rows if r["source"].strip()!="REPRESENTAÇÕES DOS ECERAE (Ecerae eimamomo)"]
 if path.name=="jakomeaJiwu.txt":
  rows=[r for r in rows if not r["source"].startswith("COMENTÁRIO De COQUEIRO")]
 if path.name=="ciriloDiscurso.txt":
  raw=path.read_text(encoding="utf-8-sig").replace("\\r\\n","\\n").replace("\\r","\\n")
  m=re.search(r"(?s)(Pao rakojere oino woje\\..+?)\\n\\s*1\\.\\s*(.+?)\\n\\s*2\\.",raw)
  if m and rows:
   rows[0]["source"]=m.group(1).strip(); rows[0]["portuguese"]=m.group(2).strip(); rows[0]["editorial_note"]="Initial unnumbered Bororo block aligned with the following Portuguese unit 1."
  for r in rows:
   marker="\\nEntão ele colocou uma madeira"
   if r["source_number"]=="2" and not r["portuguese"] and marker in r["source"]:
    r["source"],tail=r["source"].split(marker,1); r["portuguese"]="Então ele colocou uma madeira"+tail; r["editorial_note"]="Portuguese translation follows Bororo without a repeated number."
 for i,r in enumerate(rows,1): r["witness_id"]=f"{key}.{i:03d}"
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
