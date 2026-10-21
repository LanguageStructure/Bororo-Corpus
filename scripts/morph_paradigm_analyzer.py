#!/usr/bin/env python3
"""Analisador paradigmático conservador: somente análises atestadas no CoNLL-U.

Uso:
 python3 scripts/morph_paradigm_analyzer.py --form iture
 python3 scripts/morph_paradigm_analyzer.py --lemma tu
 python3 scripts/morph_paradigm_analyzer.py --evaluate
"""
import argparse,csv,json
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"tokenizer_morph_paradigms.tsv"
TARGET={"tu","mako","ako","kodu","mugu"}
def load():
    by_form=defaultdict(list);by_lemma=defaultdict(list)
    with INDEX.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f,delimiter="\t"):
            if row["lemma"] not in TARGET or row["upos"]!="VERB":continue
            item={"form":row["form"],"lemma":row["lemma"],"upos":row["upos"],
                  "feats":row["feats"],"frequency":int(row["frequency"]),"evidence":"attested"}
            by_form[row["form"]].append(item);by_lemma[row["lemma"]].append(item)
    return by_form,by_lemma
def evaluate(by_form):
    seen=total=matched=0;unknown=Counter()
    with (ROOT/"CorBo/Corpus_Files/CorBo.conllu").open(encoding="utf-8-sig") as f:
        for line in f:
            cols=line.rstrip("\r\n").split("\t")
            if len(cols)!=10 or not cols[0].isdigit():continue
            form,lemma,upos=cols[1].casefold(),cols[2].casefold(),cols[3]
            if lemma not in TARGET or upos!="VERB":continue
            total+=1
            analyses=by_form.get(form,[])
            if analyses:seen+=1
            if any(a["lemma"]==lemma and a["upos"]==upos for a in analyses):matched+=1
            else:unknown[form]+=1
    return {"evaluation":"in_sample_attestation_only_not_predictive_accuracy",
            "target_lemmas":sorted(TARGET),"target_tokens":total,
            "tokens_with_attested_form":seen,"tokens_with_matching_lemma_upos":matched,
            "unmatched_forms":unknown.most_common(30),
            "warning":"O mesmo corpus alimenta o índice e a avaliação; não mede generalização nem acurácia."}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--form");g.add_argument("--lemma");g.add_argument("--evaluate",action="store_true")
    args=p.parse_args()
    by_form,by_lemma=load()
    if args.evaluate:result=evaluate(by_form)
    elif args.form:result={"query":args.form,"analyses":sorted(by_form.get(args.form.casefold(),[]),key=lambda x:-x["frequency"])}
    else:result={"query":args.lemma,"forms":sorted(by_lemma.get(args.lemma.casefold(),[]),key=lambda x:-x["frequency"])}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
