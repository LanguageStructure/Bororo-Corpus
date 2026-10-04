#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import selected additional Bororo documentary witnesses as a conservative review batch."""
from __future__ import annotations
import csv,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
SPECS=[
 ("aijedoge.txt","AIJ","Aijedoge",None),
 ("barujauwo.txt","BARU","Barujauwo",None),
 ("primeirasAndanca.txt","PAND","Primeiras Andanças",None),
 ("gemeosBakororodoge.txt","GBAK","Gêmeos Bakororodoge",None),
 ("butoriku.txt","BUT","Parijura mata o monstro Butoriku",30),
]
FIELDS=["id","document","source_file","source_number","section","source","reviewed","portuguese","editorial_note"]

def numbered(line):
 m=re.match(r"^\s*(\d{1,3})\s*[.)]?\s*(.*\S)?\s*$",line)
 return (m.group(1), (m.group(2) or "").strip()) if m else None

def heading(s):
 return bool(s and not numbered(s) and len(s)<180 and re.search(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]",s)
             and s.upper()==s and not re.search(r"[.!?]$",s))

def numbered_heading(s):
 # Section headings may themselves be numbered, e.g.
 # "1.PARIJURA MATA O MONSTRO..." or "2.AROGIAREUDO E SEU FILHO JURE".
 m=re.match(r"^\s*\d{1,3}\s*[.)]\s*(.+?)\s*$",s)
 if not m: return False
 body=m.group(1)
 return bool(len(body)<180 and re.search(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]",body)
             and body.upper()==body and not re.search(r"[.!?]$",body))

def parse(path,key,title,max_source_number=None):
 lines=path.read_text(encoding="utf-8-sig").replace("\r\n","\n").replace("\r","\n").splitlines()
 rows=[]; section=""; i=0
 while i<len(lines):
  s=lines[i].strip()
  if not s: i+=1; continue
  if numbered_heading(s) or heading(s):
   section=s; i+=1; continue
  a=numbered(s)
  if not a: i+=1; continue
  n,bor=a; i+=1
  # Optional documentary cutoff: useful when a source file continues with
  # material that overlaps another witness and must not be duplicated.
  if max_source_number is not None and int(n) > max_source_number:
   break
  # Collect the Bororo block until the same source number reappears.
  # In these witnesses the Portuguese translation may follow after one or
  # more continuation lines rather than being immediately adjacent.
  bor_lines=[bor] if bor else []
  por_lines=[]; j=i; paired=False
  while j<len(lines):
   t=lines[j].strip()
   if not t: j+=1; continue
   b=numbered(t)
   if b:
    if b[0]==n:
     por_lines=[b[1]] if b[1] else []
     j+=1; paired=True
     # Translation continuation ends at the next numbered unit/heading.
     while j<len(lines):
      u=lines[j].strip()
      if not u: j+=1; continue
      if numbered(u) or heading(u): break
      por_lines.append(u); j+=1
     i=j
    break
   if heading(t): break
   bor_lines.append(t); j+=1
  if not paired:
   i=j
  rows.append({"id":f"{key}.{len(rows)+1:03d}","document":title,"source_file":path.name,
               "source_number":n,"section":section,"source":"\\n".join(bor_lines).strip(),
               "reviewed":"","portuguese":"\\n".join(por_lines).strip(),
               "editorial_note":""})
 return rows

def main():
 if len(sys.argv)!=2:
  raise SystemExit("Uso: python3 scripts/import_archive_additions.py '/caminho/Bororo Corpus'")
 base=Path(sys.argv[1]).expanduser().resolve()
 if not base.is_dir(): raise SystemExit(f"Diretório não encontrado: {base}")
 allrows=[]
 for fn,key,title,max_source_number in SPECS:
  p=base/fn
  if not p.exists(): raise SystemExit(f"Arquivo obrigatório não encontrado: {p}")
  rows=parse(p,key,title,max_source_number=max_source_number)
  if not rows: raise SystemExit(f"Nenhuma unidade numerada encontrada em {fn}")
  print(f"{fn}: {len(rows)} unidades")
  allrows.extend(rows)
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(allrows)
 print(f"OK: {len(allrows)} unidades -> {OUT.relative_to(ROOT)}")
 print("As fontes permanecem inalteradas; alinhamentos foram criados somente quando o mesmo número reaparece como tradução; continuações são preservadas.")

if __name__=="__main__": main()
