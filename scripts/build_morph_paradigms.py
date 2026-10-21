#!/usr/bin/env python3
"""Índice paradigmático atestado FORM–LEMMA–UPOS–FEATS do CorBo.

Não inventa limites morfológicos nem interpreta '_' como categoria.
Uso: python3 scripts/build_morph_paradigms.py
"""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
OUT=ROOT/"tokenizer_morph_paradigms.tsv"
REPORT=ROOT/"tokenizer_morph_paradigms_summary.json"
def main():
    paradigms=defaultdict(Counter)
    missing=Counter()
    for line in SOURCE.open(encoding="utf-8-sig"):
        c=line.rstrip("\r\n").split("\t")
        if len(c)!=10 or not c[0].isdigit():continue
        form,lemma,upos,feats=c[1],c[2],c[3],c[5]
        if form in ("","_"):continue
        if lemma in ("","_"):
            missing["missing_lemma"]+=1
            continue
        paradigms[(lemma.casefold(),upos if upos!="_" else "")][(form.casefold(),feats if feats!="_" else "")]+=1
    rows=[]
    for (lemma,upos),observations in paradigms.items():
        forms={form for form,_ in observations}
        total=sum(observations.values())
        for (form,feats),n in observations.items():
            rows.append({"lemma":lemma,"upos":upos,"form":form,"feats":feats,"frequency":n,
                         "paradigm_distinct_forms":len(forms),"paradigm_tokens":total})
    rows.sort(key=lambda r:(-r["paradigm_tokens"],r["lemma"],r["upos"],-r["frequency"],r["form"],r["feats"]))
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["lemma","upos","form","feats","frequency","paradigm_distinct_forms","paradigm_tokens"],delimiter="\t")
        w.writeheader();w.writerows(rows)
    summary={"schema":"corbo-morph-paradigms/v1","source":str(SOURCE.relative_to(ROOT)),
             "paradigms":len(paradigms),"paradigms_with_multiple_forms":sum(len({form for form,_ in obs})>1 for obs in paradigms.values()),
             "attested_form_feature_combinations":len(rows),
             "tokens_with_lemma":sum(sum(obs.values()) for obs in paradigms.values()),
             "tokens_without_lemma":missing["missing_lemma"],
             "note":"Paradigmas agrupados por lema e UPOS; não constituem segmentações validadas."}
    REPORT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("Índice:",OUT.name)
if __name__=="__main__":main()
