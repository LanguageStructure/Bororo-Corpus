#!/usr/bin/env python3
"""Gera índice morfológico integrado para consulta, sem alterar dados existentes.

Uso: python3 scripts/build_morph_integrated_index.py
Saída: docs/data/morph-integrated-index.json
"""
import csv,json,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from morph_analyzer_v2 import analyze
INDEX=ROOT/"tokenizer_morph_paradigms.tsv"
OUT=ROOT/"docs/data/morph-integrated-index.json"
def build():
    lexical=defaultdict(list)
    with INDEX.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f,delimiter="\t"):
            lexical[row["form"].casefold()].append({
                "lemma":row["lemma"],"upos":row["upos"] or None,
                "feats":row["feats"] or None,"frequency":int(row["frequency"])
            })
    # The paradigm index omits occurrences without lemma. Read the corpus
    # directly to include ALL types and accurate token frequencies.
    forms=defaultdict(int)
    corpus=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
    with corpus.open(encoding="utf-8-sig") as f:
        for line in f:
            c=line.rstrip("\r\n").split("\t")
            if len(c)==10 and c[0].isdigit() and c[1] not in ("","_"):
                forms[c[1].casefold()]+=1
    records=[]
    for form,freq in sorted(forms.items()):
        analyses=analyze(form)["analyses"]
        records.append({
            "form":form,"frequency":freq,
            "lexical_evidence":sorted(lexical.get(form,[]),key=lambda x:-x["frequency"]),
            "morphological_segmentations":[{
                "segments":a["segments"],"proposed_stem_lemma":a["lemma"],
                "status":a["status"],"surface_matches":a["surface_matches"]
            } for a in analyses]
        })
    result={
        "schema":"corbo-morph-integrated/v1",
        "source":"CorBo/Corpus_Files/CorBo.conllu",
        "notes":[
            "LEXICAL: lema/UPOS/FEATS são evidências CoNLL-U; não são fronteiras morfológicas.",
            "MORPHOLOGY: segmentações são independentes do lema lexical.",
            "Status hypothesis não implica validação; ausência de análise é permitida.",
            "Formas são agrupadas sem distinção de maiúsculas/minúsculas."
        ],
        "stats":{"types":len(records),"tokens":sum(forms.values()),
                 "types_with_lexical_evidence":sum(bool(r["lexical_evidence"]) for r in records),
                 "types_with_segmentation":sum(bool(r["morphological_segmentations"]) for r in records)},
        "entries":records
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print(json.dumps(result["stats"],ensure_ascii=False,indent=2))
    print("Índice:",OUT.relative_to(ROOT))
if __name__=="__main__":
    build()
