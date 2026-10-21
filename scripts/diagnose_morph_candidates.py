#!/usr/bin/env python3
"""Diagnóstico reproduzível de formas sem candidatos e ambiguidades do CorBo."""
import csv,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CORPUS=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
CANDIDATES=ROOT/"tokenizer_morph_candidates.tsv"
def main():
    forms=Counter()
    with CORPUS.open(encoding="utf-8-sig") as f:
        for line in f:
            c=line.rstrip("\r\n").split("\t")
            if len(c)==10 and c[0].isdigit() and c[1] not in ("","_"):
                forms[c[1].casefold()]+=1
    options={}
    with CANDIDATES.open(encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f,delimiter="\t"):
            options.setdefault(row["form"],[]).append(row)
    missing=[{"form":form,"frequency":n} for form,n in forms.most_common() if form.isalpha() and form not in options]
    ambiguous=[{"form":form,"frequency":forms[form],"candidate_count":len(rows),"candidates":" ; ".join(r["candidate"] for r in rows)} for form,rows in options.items() if len(rows)>1]
    ambiguous.sort(key=lambda r:(-r["frequency"],r["form"]))
    for filename,rows,columns in [
        ("tokenizer_morph_unanalysed_top100.tsv",missing[:100],["form","frequency"]),
        ("tokenizer_morph_ambiguous_top100.tsv",ambiguous[:100],["form","frequency","candidate_count","candidates"])]:
        with (ROOT/filename).open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=columns,delimiter="\t");w.writeheader();w.writerows(rows)
    print("Formas alfabéticas sem candidato:",len(missing))
    print("Formas com múltiplos candidatos:",len(ambiguous))
    print("\n20 formas frequentes sem candidato:")
    for row in missing[:20]:print("{:<25} {:>6}".format(row["form"],row["frequency"]))
    print("\nArquivos: tokenizer_morph_unanalysed_top100.tsv; tokenizer_morph_ambiguous_top100.tsv")
if __name__=="__main__":main()
