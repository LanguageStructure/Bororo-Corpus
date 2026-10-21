#!/usr/bin/env python3
"""Consulta lexical + segmentação, sem equiparar lema a morfema.

Requer tokenizer_morph_paradigms.tsv gerado por build_morph_paradigms.py.
Uso: python3 scripts/morph_lexical_analysis.py --form icare
"""
import argparse,csv,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from morph_analyzer_v2 import analyze as segment
INDEX=ROOT/"tokenizer_morph_paradigms.tsv"
def lexical_evidence(form):
    rows=[]
    with INDEX.open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f,delimiter="\t"):
            if r["form"].casefold()==form.casefold():
                rows.append({"lemma":r["lemma"],"upos":r["upos"] or None,
                             "feats":r["feats"] or None,"frequency":int(r["frequency"])})
    rows.sort(key=lambda r:(-r["frequency"],r["lemma"],r["upos"] or ""))
    return rows
def analyze(form):
    lexical=lexical_evidence(form)
    hypotheses=segment(form)["analyses"]
    return {"form":form,"lexical_evidence":lexical,
            "morphological_segmentations":[{
                "segments":h["segments"],"proposed_stem_lemma":h["lemma"],
                "segmentation_status":h["status"],
                "surface_matches":h["surface_matches"],
                "note":"proposed_stem_lemma é rótulo da base, não substitui LEMMA do CoNLL-U"
            } for h in hypotheses],
            "interpretation":"UPOS/LEMMA/FEATS são evidências do CoNLL-U; segmentações são independentes. Ausência de evidência não significa análise inválida."}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--form",required=True)
    args=p.parse_args()
    print(json.dumps(analyze(args.form),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
