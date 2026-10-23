#!/usr/bin/env python3
"""Gera índice morfológico integrado para consulta, sem alterar dados existentes.

Uso: python3 scripts/build_morph_integrated_index.py
Saída: docs/data/morph-integrated-index.json
"""
import argparse,json,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from morph_analyzer_v2 import analyze
INDEX=ROOT/"tokenizer_morph_paradigms.tsv"
OUT=ROOT/"docs/data/morph-integrated-index.json"
def build(corpus=None, output=None):
    # Extrai evidências diretamente do mesmo CoNLL-U usado para frequências.
    # Não depende de TSV intermediário potencialmente desatualizado.
    lexical_counts=defaultdict(lambda:defaultdict(int))
    forms=defaultdict(int)
    corpus=Path(corpus) if corpus else ROOT/"CorBo/Corpus_Files/CorBo.conllu"
    if not corpus.is_file():
        raise FileNotFoundError(f"Corpus não encontrado: {corpus}")
    output=Path(output) if output else OUT
    with corpus.open(encoding="utf-8-sig") as f:
        for line in f:
            c=line.rstrip("\r\n").split("\t")
            if len(c)!=10 or not c[0].isdigit() or c[1] in ("","_"):
                continue
            form=c[1].casefold()
            forms[form]+=1
            lemma,upos,feats=c[2],c[3],c[5]
            if lemma not in ("","_"):
                lexical_counts[form][(lemma.casefold(),None if upos=="_" else upos,
                                      None if feats=="_" else feats)]+=1
    lexical={}
    for form,counts in lexical_counts.items():
        lexical[form]=sorted(
            ({"lemma":lemma,"upos":upos,"feats":feats,"frequency":n}
             for (lemma,upos,feats),n in counts.items()),
            key=lambda r:(-r["frequency"],r["lemma"],r["upos"] or "")
        )
    if not forms:
        raise RuntimeError("Nenhum token CoNLL-U encontrado: verifique separadores TAB e caminho do corpus. Índice NÃO gerado.")
    records=[]
    for form,freq in sorted(forms.items()):
        analyses=analyze(form)["analyses"]
        records.append({
            "form":form,"frequency":freq,
            "lexical_evidence":sorted(lexical.get(form,[]),key=lambda x:-x["frequency"]),
            "morphological_segmentations":[{
                "segments":a["segments"],"proposed_stem_lemma":a["lemma"],
                "status":a["status"],"surface_matches":a["surface_matches"],
                **({"surface_segments":a["surface_segments"]} if "surface_segments" in a else {}),
                **({"morphophonology":a["morphophonology"]} if "morphophonology" in a else {})
            } for a in analyses]
        })
    result={
        "schema":"corbo-morph-integrated/v1",
        "source":str(corpus.resolve().relative_to(ROOT)) if ROOT in corpus.resolve().parents else str(corpus.resolve()),
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
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print(json.dumps(result["stats"],ensure_ascii=False,indent=2))
    print("Índice:",output)
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus",type=Path,help="Arquivo CoNLL-U de entrada (padrão: CorBo.conllu)")
    parser.add_argument("--output",type=Path,help="JSON de saída")
    args=parser.parse_args()
    build(args.corpus,args.output)
