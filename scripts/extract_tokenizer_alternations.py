#!/usr/bin/env python3
"""Extract FORM/LEMMA/FEATS correspondences and conservative alternation candidates.

No inferred segmentation is called gold. Reads canonical CoNLL-U without
modifying it. Output is TSV for linguistic review.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse, csv

PREFIXES=("ce","pa","ta","tu","i","a","u","e")
ENDINGS=("modukare","modure","kare","re","wo","ie","iagu","ia","rogu")
def rows(path):
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            if line.startswith("#") or not line.strip():continue
            c=line.rstrip("\n").split("\t")
            if len(c)==10 and c[0].isdigit() and c[1]!="_" and c[2]!="_":
                yield c[1].casefold(),c[2].casefold(),c[3],c[5]

def align(form,lemma):
    """Surface alignment hypothesis, not morpheme analysis."""
    candidates=[]
    for prefix in ("",*PREFIXES):
        if prefix and not form.startswith(prefix):continue
        for ending in ("",*ENDINGS):
            if ending and not form.endswith(ending):continue
            if len(form)<=len(prefix)+len(ending):continue
            core=form[len(prefix):len(form)-len(ending) if ending else len(form)]
            if len(core)<2:continue
            # Do not license a lexical alternation just because it resembles
            # a suffix; report its surface and lemma for human assessment.
            if core==lemma: grade=0
            elif core=="mago" and lemma=="mako" and prefix: grade=1
            elif core=="wiapaga" and lemma=="biapaga" and prefix:grade=1
            else:grade=2
            candidates.append((grade,len(prefix)+len(ending),prefix,core,ending))
    if not candidates:return ("",form,"","unresolved")
    candidates.sort(key=lambda x:(x[0],x[1],x[2],x[4]))
    grade,_,prefix,core,ending=candidates[0]
    return prefix,core,ending,("exact_base" if grade==0 else "curated_allomorph" if grade==1 else "unresolved")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",default="CorBo/Corpus_Files/CorBo.conllu")
    ap.add_argument("--out",default="reports/tokenizer-v2/alternations.tsv")
    args=ap.parse_args()
    observed=Counter(rows(Path(args.corpus)))
    output=Path(args.out);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,delimiter="\t")
        w.writerow(["form","lemma","upos","feats","frequency","prefix_candidate",
                    "surface_base_candidate","ending_candidate","alignment_status"])
        for (form,lemma,upos,feats),freq in sorted(observed.items(),key=lambda x:(-x[1],x[0])):
            prefix,base,ending,status=align(form,lemma)
            w.writerow([form,lemma,upos,feats,freq,prefix,base,ending,status])
    print(f"{len(observed)} FORM/LEMMA/UPOS/FEATS combinations -> {output}")
if __name__=="__main__":main()
