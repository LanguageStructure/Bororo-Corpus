#!/usr/bin/env python3
"""Extrai contextos atestados para investigar alternâncias morfofonológicas.

Não infere regras gerais e não modifica o corpus.
Uso: python3 scripts/export_morphophonology_contexts.py
"""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
OUTPUT=ROOT/"tokenizer_morphophonology_contexts.tsv"
TARGETS={
    "inagore":("ako","nago","i+nago+re"),
    "cenagore":("ako","nago","cen+ako+re"),
    "egore":("ako","gore","e+ako+re"),
    "cegodure":("kodu","godu","ce+kodu+re"),
    "cedaregodure":("ce","ced","ce+are+godu+re"),
}
FIELDS=["form","base","observed_sequence","confirmed_segmentation","sent_id",
        "text","text_por","text_eng","left_context","right_context",
        "lemma","upos","feats","analysis_note"]
def main():
    rows=[];meta={};tokens=[]
    def flush():
        for i,t in enumerate(tokens):
            form=t["form"].casefold()
            if form not in TARGETS:continue
            base,observed,segments=TARGETS[form]
            rows.append(dict(form=t["form"],base=base,observed_sequence=observed,
                confirmed_segmentation=segments,sent_id=meta.get("sent_id",""),
                text=meta.get("text",""),text_por=meta.get("text_por",""),
                text_eng=meta.get("text_eng",""),
                left_context=" ".join(x["form"] for x in tokens[max(0,i-5):i]),
                right_context=" ".join(x["form"] for x in tokens[i+1:i+6]),
                lemma=t["lemma"],upos=t["upos"],feats=t["feats"],analysis_note=""))
    with SOURCE.open(encoding="utf-8-sig") as f:
        for raw in f:
            line=raw.rstrip("\r\n")
            if not line:
                flush();meta={};tokens=[];continue
            if line.startswith("#"):
                if "=" in line:
                    k,v=line[1:].split("=",1);meta[k.strip()]=v.strip()
                continue
            c=line.split("\t")
            if len(c)==10 and c[0].isdigit():
                tokens.append(dict(form=c[1],lemma=c[2],upos=c[3],feats=c[5]))
        flush()
    if not rows:
        raise RuntimeError("Nenhuma ocorrência encontrada; confira o CoNLL-U.")
    with OUTPUT.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t")
        writer.writeheader();writer.writerows(rows)
    print("Ocorrências exportadas:",len(rows))
    for form in TARGETS:
        subset=[r for r in rows if r["form"].casefold()==form]
        print(form,len(subset))
        for row in subset[:2]:
            print(" ",row["sent_id"],"|",row["text"][:130])
    print("Arquivo:",OUTPUT.name)
if __name__=="__main__":main()
