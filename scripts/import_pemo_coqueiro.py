#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import the Frederico Coqueiro Pemo witness (Meruri, 1974) for editorial review."""
from __future__ import annotations
import csv,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"

def main():
    if len(sys.argv)!=2: raise SystemExit("Uso: python3 scripts/import_pemo_coqueiro.py /caminho/PemoCoqueiro.txt")
    src=Path(sys.argv[1]).expanduser().resolve()
    if not src.exists(): raise SystemExit(f"Arquivo não encontrado: {src}")
    lines=src.read_text(encoding="utf-8").replace("\r\n","\n").splitlines()
    rows=[]; section=""; i=0
    while i<len(lines):
        s=lines[i].strip()
        if not s: i+=1; continue
        # Headings are retained as metadata and never promoted to corpus sentences.
        if re.match(r"^(?:\d+\.?\s*)?[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ,:;()'’–—-]{5,}$",s):
            section=s; i+=1; continue
        m=re.match(r"^(\d{1,3})[.)]?\s*(.*)$",s)
        if not m: i+=1; continue
        n=m.group(1); first=m.group(2).strip(); i+=1
        # Conservative pairing: only an immediately following line with the same number is accepted as Portuguese.
        bor=[first]; por=""
        while i<len(lines) and not lines[i].strip(): i+=1
        if i<len(lines):
            p=re.match(r"^"+re.escape(n)+r"[.)]?\s*(.*)$",lines[i].strip())
            if p: por=p.group(1).strip(); i+=1
        rows.append({"id":f"PC.{len(rows)+1:03d}","source_number":n,"section":section,"source":first,
                     "reviewed":"","portuguese":por,"editorial_note":""})
    # Documentary repair pass. Some translations in this witness carry the same
    # source number as the Bororo unit and were therefore parsed as a second unit.
    # Merge only rows whose second member is overtly Portuguese.
    pt_prefixes=(
        "o nosso","disse:","eles diziam","as mulheres","eles perguntaram",
        "depois (","então ela","eis que","o que ","aí ","ao ","logo ",
        "foram ","ele ","ela ","os ","as ","você ","eu ","nós "
    )
    def overt_portuguese(s):
        return s.strip().casefold().startswith(pt_prefixes)
    repaired=[]; k=0
    while k<len(rows):
        r=rows[k]
        # Explicit documentary inline translations in the source witness.
        # Source numbers 3–10 have "Bororo – Portuguese" on one numbered line.
        if not r["portuguese"] and r["source_number"] in {str(x) for x in range(3,11)}:
            for marker,prefix in ((" – Eis que ","Eis que "),(" – Ei que ","Ei que ")):
                if marker in r["source"]:
                    bor,pt=r["source"].split(marker,1)
                    r["source"]=bor.strip()
                    r["portuguese"]=(prefix+pt).strip()
                    r["editorial_note"]="Portuguese translation occurs inline after an en dash in the numbered source unit."
                    break
        # Source number 143 contains the short Bororo prompt followed inline by Portuguese.
        if not r["portuguese"] and r["source_number"]=="143":
            marker=" Então ela disse:"
            if marker in r["source"]:
                bor,pt=r["source"].split(marker,1)
                r["source"]=bor.strip()
                r["portuguese"]=("Então ela disse:"+pt).strip()
                r["editorial_note"]="Portuguese translation occurs inline in source number 143."
        if k+1<len(rows):
            q=rows[k+1]
            same=(q["source_number"]==r["source_number"])
            qsrc=q["source"].strip()
            if same and not r["portuguese"] and overt_portuguese(qsrc):
                r["portuguese"]=qsrc
                r["editorial_note"]="Portuguese translation carries the same source number and was merged during documentary import."
                repaired.append(r); k+=2; continue
        repaired.append(r); k+=1
    # Preserve the originally assigned editorial IDs. Merged translation-only
    # rows intentionally leave gaps; stable IDs take precedence over continuity.
    rows=repaired

    if not rows: raise SystemExit("Importação interrompida: nenhuma unidade numerada encontrada.")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=["id","source_number","section","source","reviewed","portuguese","editorial_note"]
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
    print(f"OK: {len(rows)} unidades documentais -> {OUT.relative_to(ROOT)}")
    print("Pares de mesmo número com tradução portuguesa explícita são fundidos documentalmente.")
    print("Somente traduções com o mesmo número imediatamente adjacente foram alinhadas automaticamente.")
    print("A fonte PemoCoqueiro.txt permanece inalterada.")

if __name__=="__main__": main()
