#!/usr/bin/env python3
"""Exporta contextos de formas controversas para revisão linguística.

Uso: python3 scripts/export_morph_conflict_contexts.py
Gera TSV local; não modifica CoNLL-U nem publica dados de trabalho.
"""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
OUTPUT=ROOT/"tokenizer_morph_conflict_contexts.tsv"
TARGETS={"padui","tududo","ituiagu"}
def main():
    rows=[]
    meta={}
    tokens=[]
    def flush():
        for i,token in enumerate(tokens):
            if token["form"].casefold() not in TARGETS:continue
            rows.append({
                "form":token["form"],"sent_id":meta.get("sent_id",""),
                "text":meta.get("text",""),"text_por":meta.get("text_por",""),
                "text_eng":meta.get("text_eng",""),
                "left_context":" ".join(t["form"] for t in tokens[max(0,i-6):i]),
                "right_context":" ".join(t["form"] for t in tokens[i+1:i+7]),
                "lemma":token["lemma"],"upos":token["upos"],
                "feats":token["feats"],"misc":token["misc"],
                "reviewed_lemma":"","reviewed_segments":"","review_note":""
            })
    with SOURCE.open(encoding="utf-8-sig") as f:
        for line in f:
            line=line.rstrip("\r\n")
            if not line:
                flush();meta={};tokens=[];continue
            if line.startswith("#") and "=" in line:
                key,val=line[1:].split("=",1);meta[key.strip()]=val.strip()
            elif not line.startswith("#"):
                c=line.split("\t")
                if len(c)==10 and c[0].isdigit():
                    tokens.append({"form":c[1],"lemma":c[2],"upos":c[3],
                                   "feats":c[5],"misc":c[9]})
        flush()
    fields=["form","sent_id","text","text_por","text_eng","left_context","right_context",
            "lemma","upos","feats","misc","reviewed_lemma","reviewed_segments","review_note"]
    with OUTPUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t");w.writeheader();w.writerows(rows)
    print("Ocorrências:",len(rows))
    for form in sorted(TARGETS):
        subset=[r for r in rows if r["form"].casefold()==form]
        print("\n"+form+": "+str(len(subset))+" ocorrência(s)")
        for r in subset[:4]:
            print(" ",r["sent_id"],"|",r["text"][:140],"|",r["lemma"],r["upos"])
    print("\nArquivo:",OUTPUT.name)
if __name__=="__main__":main()
