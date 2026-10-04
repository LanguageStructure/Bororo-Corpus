#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import selected additional Bororo documentary witnesses as a conservative review batch."""
from __future__ import annotations
import csv,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv"
SPECS=[
 ("aijedoge.txt","AIJ","Aijedoge"),
 ("barujauwo.txt","BARU","Barujauwo"),
 ("primeirasAndanca.txt","PAND","Primeiras Andanças"),
 ("gemeosBakororodoge.txt","GBAK","Gêmeos Bakororodoge"),
]
FIELDS=["id","document","source_file","source_number","section","source","reviewed","portuguese","editorial_note"]

def numbered(line):
 m=re.match(r"^\s*(\d{1,3})\s*[.)]?\s*(.*\S)?\s*$",line)
 return (m.group(1), (m.group(2) or "").strip()) if m else None

def heading(s):
 return bool(s and not numbered(s) and len(s)<180 and re.search(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]",s)
             and s.upper()==s and not re.search(r"[.!?]$",s))

def parse(path,key,title):
 lines=path.read_text(encoding="utf-8-sig").replace("\r\n","\n").replace("\r","\n").splitlines()
 rows=[]; section=""; i=0
 while i<len(lines):
  s=lines[i].strip()
  if not s: i+=1; continue
  if heading(s): section=s; i+=1; continue
  a=numbered(s)
  if not a: i+=1; continue
  n,bor=a; i+=1
  # Only identical adjacent numbering licenses an automatic translation pairing.
  j=i
  while j<len(lines) and not lines[j].strip(): j+=1
  por=""
  if j<len(lines):
   b=numbered(lines[j].strip())
   if b and b[0]==n:
    por=b[1]; i=j+1
  rows.append({"id":f"{key}.{len(rows)+1:03d}","document":title,"source_file":path.name,
               "source_number":n,"section":section,"source":bor,"reviewed":"","portuguese":por,
               "editorial_note":""})
 return rows

def main():
 if len(sys.argv)!=2:
  raise SystemExit("Uso: python3 scripts/import_archive_additions.py '/caminho/Bororo Corpus'")
 base=Path(sys.argv[1]).expanduser().resolve()
 if not base.is_dir(): raise SystemExit(f"Diretório não encontrado: {base}")
 allrows=[]
 for fn,key,title in SPECS:
  p=base/fn
  if not p.exists(): raise SystemExit(f"Arquivo obrigatório não encontrado: {p}")
  rows=parse(p,key,title)
  if not rows: raise SystemExit(f"Nenhuma unidade numerada encontrada em {fn}")
  print(f"{fn}: {len(rows)} unidades")
  allrows.extend(rows)
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(allrows)
 print(f"OK: {len(allrows)} unidades -> {OUT.relative_to(ROOT)}")
 print("As fontes permanecem inalteradas; alinhamentos só foram criados para numeração adjacente idêntica.")

if __name__=="__main__": main()
