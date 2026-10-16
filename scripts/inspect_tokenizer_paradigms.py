#!/usr/bin/env python3
"""Print attested surface forms for priority lemmas, without inferring boundaries."""
from collections import Counter, defaultdict
from pathlib import Path
import argparse

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--corpus",default="CorBo/Corpus_Files/CorBo.conllu")
    p.add_argument("--lemmas",nargs="+",default=["ako","u","i","e","ji","tu","aregodu","a","eragu","kodo","apo","o","bi","karo","ai"])
    p.add_argument("--limit",type=int,default=40)
    args=p.parse_args()
    wanted=set(args.lemmas)
    counts=defaultdict(Counter)
    examples=defaultdict(lambda:defaultdict(list))
    sid=""
    with Path(args.corpus).open(encoding="utf-8-sig") as f:
        for line in f:
            if line.startswith("# sent_id ="):
                sid=line.partition("=")[2].strip()
            elif not line.strip():
                sid=""
            elif not line.startswith("#"):
                cols=line.rstrip("\n").split("\t")
                if len(cols)!=10 or not cols[0].isdigit():continue
                form,lemma,upos,feats=cols[1],cols[2].casefold(),cols[3],cols[5]
                if lemma not in wanted or upos=="PUNCT":continue
                counts[lemma][(form,upos,feats)]+=1
                if sid and len(examples[lemma][form])<3 and sid not in examples[lemma][form]:
                    examples[lemma][form].append(sid)
    for lemma in args.lemmas:
        rows=counts[lemma]
        print(f"\n### {lemma}: {sum(rows.values())} tokens; {len(set(k[0] for k in rows))} forms")
        for (form,upos,feats),n in rows.most_common(args.limit):
            print(f"{n:>5}  {form:<24} {upos:<7} {feats:<40} sent_id={','.join(examples[lemma][form])}")
if __name__=="__main__":main()
