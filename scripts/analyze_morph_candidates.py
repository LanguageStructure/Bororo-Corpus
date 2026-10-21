#!/usr/bin/env python3
"""CorBo: indução de candidatos morfológicos, sem modificar CoNLL-U.

Uso: python3 scripts/analyze_morph_candidates.py
Saídas locais: tokenizer_morph_candidates.tsv, tokenizer_morph_summary.json.
Candidatos NÃO são análises gold. As análises confirmadas prevalecem.
"""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
GOLD=ROOT/"CorBo/Corpus_Files/morph_gold_confirmed_20261021.tsv"
OUT=ROOT/"tokenizer_morph_candidates.tsv"
SUMMARY=ROOT/"tokenizer_morph_summary.json"
# Morfemas atestados nas revisões; são pistas, não regras universais.
PREFIXES=("it","in","ak","i","a","e")
SUFFIXES=("modu","mode","ka","re")
def corpus():
    forms=Counter()
    for line in SOURCE.open(encoding="utf-8-sig"):
        if not line or line.startswith("#"):continue
        c=line.rstrip("\n\r").split("\t")
        if len(c)==10 and c[0].isdigit() and c[1] not in ("","_"):
            forms[c[1].casefold()]+=1
    return forms
def confirmed():
    result=defaultdict(set)
    if not GOLD.exists():return result
    with GOLD.open(encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f,delimiter="\t"):
            # Gold por frase; não inferir correspondência entre tokens sem alinhamento.
            result[row["sent_id"]].add(row["morph_segments"])
    return result
def candidates(form,attested):
    out=[]
    for p in PREFIXES:
        if not form.startswith(p) or len(form)<=len(p)+1:continue
        stem=form[len(p):]
        if stem in attested:out.append((p+" | "+stem,"prefix",attested[stem]))
        for suf in SUFFIXES:
            if stem.endswith(suf) and len(stem)>len(suf)+1:
                core=stem[:-len(suf)]
                if core in attested:out.append((p+" | "+core+" | "+suf,"prefix+suffix",attested[core]))
    for suf in SUFFIXES:
        if form.endswith(suf) and len(form)>len(suf)+1:
            stem=form[:-len(suf)]
            if stem in attested:out.append((stem+" | "+suf,"suffix",attested[stem]))
    # Ordenação determinística. Não tomar a hipótese mais frequente como gold.
    return sorted(set(out),key=lambda x:(-x[2],x[0]))
def main():
    freq=corpus();rows=[];ambiguous=0;candidate_types=0;candidate_tokens=0
    for form,count in freq.most_common():
        options=candidates(form,freq)
        if not options:continue
        candidate_types+=1;candidate_tokens+=count
        if len(options)>1:ambiguous+=1
        for seg,rule,evidence in options:
            rows.append({"form":form,"frequency":count,"candidate":seg,
                         "rule":rule,"stem_frequency":evidence,
                         "status":"candidate_unreviewed",
                         "ambiguity_count":len(options)})
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["form","frequency","candidate","rule","stem_frequency","status","ambiguity_count"],delimiter="\t")
        w.writeheader();w.writerows(rows)
    summary={"schema":"corbo-morph-induction/v1","source":str(SOURCE.relative_to(ROOT)),
             "corpus_types":len(freq),"corpus_tokens":sum(freq.values()),
             "candidate_types":candidate_types,"candidate_tokens":candidate_tokens,
             "ambiguous_types":ambiguous,"unanalysed_types":len(freq)-candidate_types,
             "confirmed_sentence_analyses":sum(map(len,confirmed().values())),
             "warning":"Heurísticas superficiais. Não validam alternâncias b/w, p/b ou formas subjacentes. Não são gold."}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("Candidatos:",OUT,"\nResumo:",SUMMARY)
if __name__=="__main__":main()
