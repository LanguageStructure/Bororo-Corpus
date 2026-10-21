#!/usr/bin/env python3
"""Auditoria de evidências morfológicas já presentes no CoNLL-U.

Não infere segmentações nem confunde ausência de divisão com desconhecimento.
Saídas locais: tokenizer_conllu_evidence.tsv e tokenizer_conllu_evidence_summary.json.
"""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
OUT=ROOT/"tokenizer_conllu_evidence.tsv"
REPORT=ROOT/"tokenizer_conllu_evidence_summary.json"
def main():
    forms=defaultdict(Counter);tokens=0;missing=Counter();invalid=0
    for line in SRC.open(encoding="utf-8-sig"):
        c=line.rstrip("\r\n").split("\t")
        if len(c)!=10 or not c[0].isdigit():continue
        form,lemma,upos,feats=c[1],c[2],c[3],c[5]
        if form in ("","_"):continue
        tokens+=1
        for field,value in (("lemma",lemma),("upos",upos),("feats",feats)):
            if value in ("","_"):missing[field]+=1
        if feats not in ("","_") and not all("=" in part and all(part.split("=",1)) for part in feats.split("|")):invalid+=1
        forms[form.casefold()][(lemma,upos,feats)]+=1
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,delimiter="\t")
        w.writerow(["form","frequency","lemma","upos","feats","analysis_frequency","distinct_analyses","evidence_status"])
        for form,analyses in sorted(forms.items(),key=lambda kv:(-sum(kv[1].values()),kv[0])):
            total=sum(analyses.values())
            for (lemma,upos,feats),n in analyses.most_common():
                status="attested_complete" if lemma not in ("","_") and upos not in ("","_") else "attested_incomplete"
                w.writerow([form,total,lemma,upos,feats,n,len(analyses),status])
    report={"schema":"corbo-conllu-evidence/v1","source":str(SRC.relative_to(ROOT)),
            "tokens":tokens,"types":len(forms),"missing_fields_tokens":dict(missing),
            "malformed_feats_tokens":invalid,
            "forms_with_multiple_analyses":sum(len(v)>1 for v in forms.values()),
            "tokens_with_lemma_and_upos":sum(n for a in forms.values() for (l,u,_),n in a.items() if l not in ("","_") and u not in ("","_")),
            "note":"CoNLL-U fornece análises lexicais e gramaticais atestadas, mas não necessariamente fronteiras de morfemas."}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("Evidências:",OUT.name)
if __name__=="__main__":main()
