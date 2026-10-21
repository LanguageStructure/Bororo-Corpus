#!/usr/bin/env python3
"""Baseline linguístico experimental de lematização com treino sem vazamento.

Segmentos conhecidos são usados para propor vizinhos estruturais; NÃO
afirma segmentação morfológica validada nem prevê FEATS.
"""
import csv,json,random
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET={"tu","mako","ako","kodu","mugu"}
PREFIXES=("ce","pa","ta","et","tu","i","a","e","")
SUFFIXES=("modukare","modukana","moduie","modukare","modukae","modukare","modu","mode","nure","kare","kae","iagu","wo","re","do","du","i","")
def variants(word):
    seen={word}
    # Strip only a single prefix and suffix; avoid recursive over-stripping.
    for pre in PREFIXES:
        if pre and not word.startswith(pre):continue
        stem=word[len(pre):]
        seen.add(stem)
        for suf in SUFFIXES:
            if suf and stem.endswith(suf) and len(stem)>len(suf):
                seen.add(stem[:-len(suf)])
    return seen
def edit(a,b):
    row=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        new=[i]
        for j,y in enumerate(b,1):
            new.append(min(new[-1]+1,row[j]+1,row[j-1]+(x!=y)))
        row=new
    return row[-1]
def score(a,b):
    va=variants(a);vb=variants(b)
    return min(edit(x,y) for x in va for y in vb)
def main():
    groups=defaultdict(lambda:defaultdict(int))
    with (ROOT/"tokenizer_morph_paradigms.tsv").open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f,delimiter="\t"):
            if r["lemma"] in TARGET and r["upos"]=="VERB":
                groups[r["lemma"]][r["form"]]+=int(r["frequency"])
    rng=random.Random(20261021);test=[]
    for lemma,forms in sorted(groups.items()):
        keys=sorted(forms);rng.shuffle(keys)
        test.extend((lemma,form,forms[form]) for form in sorted(keys[:max(1,len(keys)//5)]))
    held={f for _,f,_ in test}
    train={l:sorted(f for f in forms if f not in held) for l,forms in groups.items()}
    # Cache variants to keep runtime low.
    cache={f:variants(f) for forms in train.values() for f in forms}
    cache.update({f:variants(f) for _,f,_ in test})
    def cached_score(a,b):
        return min(edit(x,y) for x in cache[a] for y in cache[b])
    results=[];correct=covered=weighted_correct=weighted_covered=0
    for lemma,form,n in test:
        candidates=[]
        for label,forms in train.items():
            for known in forms:
                candidates.append((cached_score(form,known),label,known))
        bestdist=min(x[0] for x in candidates)
        labels=sorted({x[1] for x in candidates if x[0]==bestdist})
        pred=labels[0] if len(labels)==1 and bestdist<=1 else None
        ok=pred==lemma
        correct+=ok;covered+=pred is not None
        weighted_correct+=n*ok;weighted_covered+=n*(pred is not None)
        results.append({"form":form,"gold_lemma":lemma,"frequency":n,
                        "predicted_lemma":pred,"distance":bestdist,"tied_lemmas":labels,"correct":ok})
    total=sum(n for _,_,n in test)
    summary={"schema":"corbo-morph-rule-baseline/v1","heldout_types":len(test),"heldout_tokens":total,
             "correct_types":correct,"covered_types":covered,
             "type_accuracy":correct/len(test) if test else None,
             "type_coverage":covered/len(test) if test else None,
             "type_precision":correct/covered if covered else None,
             "token_accuracy":weighted_correct/total if total else None,
             "token_coverage":weighted_covered/total if total else None,
             "method":"prefix/suffix stripping + edit distance <=1, abstain on ties",
             "warning":"Experimental: morpheme boundaries and allomorphy are hypotheses; no segmentation or FEATS prediction."}
    out=ROOT/"tokenizer_morph_rule_evaluation.json"
    out.write_text(json.dumps({"summary":summary,"predictions":results},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("Previsões:",out.name)
if __name__=="__main__":main()
