#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Importa o testemunho textual Bakaru Maiwu (NT_Ochoa.txt).

A fonte nunca é normalizada. O script separa livros e capítulos e cria TSVs
editoriais por livro. A segmentação em versículos só é feita quando o número
está explicitamente unido ao início do texto (p.ex. 12Itaidure); casos
ambíguos permanecem como unidades documentais para revisão.
"""
from __future__ import annotations
import csv,re,sys,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"CorBo_vNext/texts/bakaru-maiwu"
BOOKS=[
("MATEUS","MAT","mateus"),("MARCOS","MRK","marcos"),("LUCAS","LUK","lucas"),
("JOÃO","JHN","joao"),("ATOS DOS APÓSTLOS","ACT","atos"),("ROMANOS","ROM","romanos"),
("I. CORINTIOS","1CO","1-corintios"),("I I. CORÍNTIOS","2CO","2-corintios"),
("GALATAS","GAL","galatas"),("EFÉSIOS","EPH","efesios"),("FILIPENSES","PHP","filipenses"),
("COLOSSENSES","COL","colossenses"),("I. TESSALONICENSES","1TH","1-tessalonicenses"),
("I I .TESSALONICENSES","2TH","2-tessalonicenses"),("I TIMÓTEO","1TI","1-timoteo"),
("I I TIMOTEO","2TI","2-timoteo"),("TITO","TIT","tito"),("FILEMON","PHM","filemon"),
("HEBREOS","HEB","hebreus"),("TIAGO","JAS","tiago"),("I. PEDRO","1PE","1-pedro"),
("II. PEDRO","2PE","2-pedro"),("I. JOÃO","1JN","1-joao"),("II. JOÃO","2JN","2-joao"),
("III. JOÃO","3JN","3-joao"),("JUDAS","JUD","judas"),("APOCALIPSE","REV","apocalipse")]
HEAD={x[0]:x for x in BOOKS}
FIELDS=["id","book","book_code","chapter","verse","source","reviewed","editorial_note"]

def split_books(text):
 lines=text.splitlines(); starts=[]
 for i,l in enumerate(lines):
  s=l.strip()
  if s in HEAD: starts.append((i,s))
 if len(starts)!=27: raise SystemExit(f"Esperados 27 livros; encontrados {len(starts)}")
 for n,(i,h) in enumerate(starts):
  j=starts[n+1][0] if n+1<len(starts) else len(lines)
  yield HEAD[h],lines[i+1:j]

def units(meta,lines):
 name,code,slug=meta
 # Conserva a linha de título editorial como metadado, não como versículo.
 while lines and not lines[0].strip(): lines=lines[1:]
 book_title=lines[0].strip() if lines else ""
 body="\n".join(lines[1:])
 # Capítulos: marcador documental no início de linha, com ou sem ponto.
 chap_re=re.compile(r"(?m)^\s*(\d{1,2})(?:\.\s*|\s+)(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")
 ms=list(chap_re.finditer(body))
 if not ms: raise SystemExit(f"Sem capítulos reconhecidos: {name}")
 out=[]
 for ci,m in enumerate(ms):
  ch=int(m.group(1)); end=ms[ci+1].start() if ci+1<len(ms) else len(body)
  chunk=body[m.end():end].strip()
  # Números de versículo aparecem colados ao primeiro caractere do versículo.
  vm=list(re.finditer(r"(?<!\d)(\d{1,3})(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ\"“])",chunk))
  if not vm:
   out.append({"id":f"BOR-CORBO-BM-{code}-{ch:03d}-DOC-001","book":name,"book_code":code,
    "chapter":str(ch),"verse":"","source":chunk,"reviewed":"","editorial_note":"Unidade documental ainda não segmentada em versículos."})
   continue
  pre=chunk[:vm[0].start()].strip()
  if pre:
   out.append({"id":f"BOR-CORBO-BM-{code}-{ch:03d}-HEAD-001","book":name,"book_code":code,
    "chapter":str(ch),"verse":"","source":pre,"reviewed":"","editorial_note":"Cabeçalho/subtítulo editorial da fonte."})
  for vi,v in enumerate(vm):
   endv=vm[vi+1].start() if vi+1<len(vm) else len(chunk)
   src=chunk[v.end():endv].strip()
   verse=v.group(1)
   out.append({"id":f"BOR-CORBO-BM-{code}-{ch:03d}-{int(verse):03d}","book":name,"book_code":code,
    "chapter":str(ch),"verse":verse,"source":src,"reviewed":"","editorial_note":""})
 return book_title,out

def main(path):
 text=Path(path).read_text(encoding="utf-8-sig")
 OUT.mkdir(parents=True,exist_ok=True)
 total=0
 for meta,lines in split_books(text):
  title,rows=units(meta,lines); name,code,slug=meta
  d=OUT/slug;d.mkdir(parents=True,exist_ok=True);p=d/f"{slug}.tsv"
  with p.open("w",encoding="utf-8",newline="") as f:
   w=csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
  (d/"source-title.txt").write_text(title+"\n",encoding="utf-8")
  print(f"{name}: {len(rows)} unidades -> {p.relative_to(ROOT)}");total+=len(rows)
 print(f"Total: {total} unidades. Fonte preservada em source; reviewed permanece vazio.")

if __name__=="__main__":
 if len(sys.argv)!=2: raise SystemExit("Uso: python3 scripts/import_bakaru_maiwu.py NT_Ochoa.txt")
 main(sys.argv[1])
