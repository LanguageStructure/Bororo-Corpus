#!/usr/bin/env python3
"""Audita hipóteses morfológicas contra FORM/LEMMA/UPOS do CoNLL-U.

Não trata ausência de lema como contradição; não usa FEATS para validar
segmentação. Uso: python3 scripts/audit_morph_analyzer.py
"""
import csv,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from morph_analyzer_v2 import analyze
CORPUS=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
OUT=ROOT/"tokenizer_morph_analyzer_audit.tsv"
SUMMARY=ROOT/"tokenizer_morph_analyzer_audit_summary.json"
def main():
    observed=defaultdict(Counter)
    for line in CORPUS.open(encoding="utf-8-sig"):
        c=line.rstrip("\r\n").split("\t")
        if len(c)!=10 or not c[0].isdigit():continue
        form,lemma,upos=c[1].casefold(),c[2].casefold(),c[3]
        if not form or form=="_":continue
        observed[form][(lemma,upos)]+=1
    rows=[];stats=Counter()
    for form,records in observed.items():
        proposals=analyze(form)["analyses"]
        lemmas={x["lemma"] for x in proposals}
        attested={lemma for lemma,upos in records if lemma not in ("","_") and upos=="VERB"}
        missing_lemma=sum(n for (lemma,upos),n in records.items() if lemma in ("","_"))
        total=sum(records.values())
        if not proposals:status="no_analysis"
        elif not attested:status="no_verbal_lemma_evidence"
        elif lemmas & attested:status="compatible"
        else:status="lemma_conflict"
        stats[status+"_types"]+=1
        stats[status+"_tokens"]+=total
        rows.append({"form":form,"tokens":total,"status":status,
                     "attested_verb_lemmas":" | ".join(sorted(attested)),
                     "proposed_lemmas":" | ".join(sorted(lemmas)),
                     "proposed_analyses":len(proposals),
                     "tokens_missing_lemma":missing_lemma})
    rows.sort(key=lambda r:(r["status"],-r["tokens"],r["form"]))
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t")
        w.writeheader();w.writerows(rows)
    summary={"schema":"corbo-morph-audit/v1","source":str(CORPUS.relative_to(ROOT)),
             "forms":len(rows),"tokens":sum(r["tokens"] for r in rows),
             "categories":dict(sorted(stats.items())),
             "caveats":[
                 "Compatível significa somente que pelo menos um lema proposto coincide com um lema verbal atestado.",
                 "Conflito indica discordância de lema, não prova erro morfológico.",
                 "FEATS, segmentação e alomorfia não são validados por esta auditoria.",
                 "Formas com múltiplas leituras podem ocorrer em diferentes categorias gramaticais."
             ]}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("Detalhes:",OUT.name)
if __name__=="__main__":main()
