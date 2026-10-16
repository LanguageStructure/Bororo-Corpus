#!/usr/bin/env python3
"""Audit v2 morphological proposals and annotated lemma paradigms.

Produces TSV reports; never modifies the source CoNLL-U.
Evidence in these reports is descriptive, not gold segmentation.
"""
from __future__ import annotations
import argparse, csv, json
from collections import Counter, defaultdict
from pathlib import Path

def load(path):
    families=defaultdict(lambda:defaultdict(Counter))
    forms=Counter()
    for line in path.open(encoding="utf-8-sig"):
        if line.startswith("#") or not line.strip():continue
        cols=line.rstrip("\n").split("\t")
        if len(cols)!=10 or not cols[0].isdigit():continue
        form,lemma,upos,feats=cols[1:6:1][0],cols[2],cols[3],cols[5]
        form=form.casefold()
        if form=="_":continue
        forms[form]+=1
        if lemma!="_":
            families[lemma.casefold()][form][(upos,feats)]+=1
    return families,forms

def write_tsv(path,fields,rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",extrasaction="ignore")
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--corpus",default="CorBo/Corpus_Files/CorBo.conllu")
    p.add_argument("--model",default="docs/data/tokenizer-v2.json")
    p.add_argument("--out",default="reports/tokenizer-v2")
    args=p.parse_args()
    families,forms=load(Path(args.corpus))
    data=json.loads(Path(args.model).read_text(encoding="utf-8"))
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    proposed=[]
    for form,record in data["analyses"].items():
        if record["status"]!="proposed":continue
        lemma=record.get("lemma","")
        family=families.get(lemma,{})
        matches=family.get(form,Counter())
        proposed.append({
            "form":form,"frequency":forms[form],
            "segments":" + ".join(record["segments"]),
            "proposed_lemma":lemma,
            "base_token_support":record.get("support",0),
            "same_lemma_form_attested":int(bool(matches)),
            "same_lemma_form_tokens":sum(matches.values()),
            "same_lemma_family_types":len(family),
            "same_lemma_family_tokens":sum(sum(c.values()) for c in family.values()),
            "annotation_analyses":"; ".join(
                f"{u}|{ft}:{n}" for (u,ft),n in matches.most_common(5))
        })
    proposed.sort(key=lambda r:(-r["frequency"],r["form"]))
    write_tsv(out/"proposals.tsv",[
        "form","frequency","segments","proposed_lemma","base_token_support",
        "same_lemma_form_attested","same_lemma_form_tokens",
        "same_lemma_family_types","same_lemma_family_tokens",
        "annotation_analyses"],proposed)
    paradigms=[]
    for lemma, family in families.items():
        for form, analyses in family.items():
            for (upos,feats),n in analyses.items():
                paradigms.append({"lemma":lemma,"form":form,"upos":upos,
                                  "feats":feats,"tokens":n,
                                  "family_types":len(family)})
    paradigms.sort(key=lambda r:(r["lemma"],-r["tokens"],r["form"]))
    write_tsv(out/"paradigms.tsv",[
        "lemma","form","upos","feats","tokens","family_types"],paradigms)
    summary={
        "proposals":len(proposed),
        "proposals_with_same_lemma_annotation":sum(r["same_lemma_form_attested"] for r in proposed),
        "lemma_families":len(families),
        "paradigm_rows":len(paradigms),
        "top_proposals":proposed[:20],
        "notes":"Proposals are hypotheses. CoNLL-U FORM/LEMMA/FEATS do not by themselves validate morpheme boundaries."
    }
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Propostas:",len(proposed),"; com correspondência FORM/LEMMA:",summary["proposals_with_same_lemma_annotation"])
    print("Famílias de lemas:",len(families),"; linhas de paradigma:",len(paradigms))
    print("Relatórios:",out)

if __name__=="__main__":main()
