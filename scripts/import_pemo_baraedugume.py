#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import Pemo e Baraedugume as a documentary editorial layer.

The source witness is never modified. The generated TSV keeps source Bororo,
Portuguese translation, section headings, and an empty reviewed layer.
"""
from __future__ import annotations
import csv,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"CorBo_vNext/texts/pemo-baraedugume/pemo_baraedugume_editorial.tsv"

def is_heading(s:str)->bool:
    return bool(re.match(r"^\d+\.\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ,–—-]+$",s.strip()))

def parse(text:str):
    lines=text.replace("\r\n","\n").splitlines(); section=""; units=[]; i=0
    while i<len(lines):
        s=lines[i].strip()
        if is_heading(s):
            section=re.sub(r"^\d+\.\s*","",s).strip(); i+=1; continue
        m=re.match(r"^(\d+)\.\s*(.*)$",s)
        if not m: i+=1; continue
        n=m.group(1); bor=[m.group(2).strip()]; i+=1
        while i<len(lines):
            t=lines[i].strip()
            if is_heading(t): break
            p=re.match(r"^"+re.escape(n)+r"\.\s*(.*)$",t)
            if p:
                por=[p.group(1).strip()]; i+=1
                while i<len(lines):
                    u=lines[i].strip()
                    if not u: i+=1; break
                    if is_heading(u) or re.match(r"^\d+\.\s*",u): break
                    por.append(u); i+=1
                units.append((n,section," ".join(bor).strip()," ".join(por).strip()))
                break
            if re.match(r"^\d+\.\s*",t): break
            if t: bor.append(t)
            i+=1
    return units

def main():
    if len(sys.argv)!=2:
        raise SystemExit("Uso: python3 scripts/import_pemo_baraedugume.py /caminho/PemoBaraedugume.txt")
    src=Path(sys.argv[1]).expanduser().resolve()
    if not src.exists(): raise SystemExit(f"Arquivo não encontrado: {src}")
    units=parse(src.read_text(encoding="utf-8"))
    if len(units)!=84:
        raise SystemExit(f"Importação interrompida: esperadas 84 unidades alinhadas; encontradas {len(units)}.")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=["id","source_number","section","source","reviewed","portuguese","editorial_note"]
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n"); w.writeheader()
        for n,section,source,portuguese in units:
            w.writerow({"id":f"PB.{int(n):03d}","source_number":n,"section":section,"source":source,
                        "reviewed":"","portuguese":portuguese,"editorial_note":""})
    print(f"OK: {len(units)} unidades -> {OUT.relative_to(ROOT)}")
    print("A fonte documental não foi alterada. Revise a coluna 'reviewed' no editor do CorBo.")

if __name__=="__main__": main()
