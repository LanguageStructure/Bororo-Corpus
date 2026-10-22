#!/usr/bin/env python3
"""Diagnóstico somente leitura da avaliação ortográfica CorBo.

Uso: python3 scripts/diagnose_orthographic_tokenizer.py
Produz JSON de contagens e TSV com exemplos de falhas de alinhamento.
Não altera o CoNLL-U nem declara que a referência é gold.
"""
import json
import unicodedata
from collections import Counter
from pathlib import Path
from evaluate_orthographic_tokenizer import ROOT, SOURCE, sentences, gold_spans, baseline, boundaries

OUT=ROOT/"tokenizer_orthographic_diagnostics.json"
EXAMPLES=ROOT/"tokenizer_orthographic_unalignable.tsv"

def normalize(s):
    return unicodedata.normalize("NFC",s)

def classify_alignment(text,tokens):
    joined=" ".join(tokens)
    if normalize(text)!=text or normalize(joined)!=joined:
        if normalize(text)==normalize(joined):
            return "unicode_normalization"
    if "".join(text.split())=="".join(joined.split()):
        return "whitespace_only"
    if normalize("".join(text.split())).casefold()==normalize("".join(joined.split())).casefold():
        return "case_or_unicode"
    stripped=lambda s:"".join(c for c in normalize(s).casefold() if c.isalnum())
    if stripped(text)==stripped(joined):
        return "punctuation_or_spacing"
    return "text_token_content_mismatch"

def classify_boundary(text,pos):
    left=text[pos-1] if pos else ""
    right=text[pos] if pos<len(text) else ""
    if left.isspace() or right.isspace():
        return "whitespace_edge"
    if left.isalnum() and right.isalnum():
        return "within_alphanumeric"
    if left in "'’-‐‑-" or right in "'’-‐‑-":
        return "apostrophe_or_hyphen"
    if not left.isalnum() or not right.isalnum():
        return "punctuation"
    return "other"

def main():
    counts=Counter();alignment=Counter();false_positive=Counter();false_negative=Counter()
    examples=[];seen=set()
    for sid,text,tokens in sentences(SOURCE):
        if text in seen:
            counts["duplicate_text"]+=1
            continue
        seen.add(text)
        gold=gold_spans(text,tokens)
        if gold is None:
            counts["unalignable"]+=1
            reason=classify_alignment(text,tokens)
            alignment[reason]+=1
            if len(examples)<300:
                examples.append((sid,reason,text," | ".join(tokens)))
            continue
        counts["aligned"]+=1
        actual=boundaries(gold)
        predicted=boundaries(baseline(text))
        if actual!=predicted:
            counts["divergent_sentences"]+=1
        for pos in predicted-actual:
            false_positive[classify_boundary(text,pos)]+=1
        for pos in actual-predicted:
            false_negative[classify_boundary(text,pos)]+=1
    result={
        "source":str(SOURCE.relative_to(ROOT)),
        "notes":"Diagnóstico heurístico; classes de alinhamento não são diagnósticos linguísticos definitivos.",
        "sentences":dict(counts),
        "unalignable_categories":dict(alignment.most_common()),
        "extra_boundary_categories":dict(false_positive.most_common()),
        "missing_boundary_categories":dict(false_negative.most_common()),
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with EXAMPLES.open("w",encoding="utf-8") as f:
        f.write("sent_id\tcategory\ttext\tconllu_tokens\n")
        for row in examples:
            f.write("\t".join(str(x).replace("\t"," ").replace("\n"," ") for x in row)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print("Exemplos:",EXAMPLES.name)
if __name__=="__main__":
    main()
