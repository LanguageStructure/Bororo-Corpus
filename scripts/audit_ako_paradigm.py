#!/usr/bin/env python3
"""Audit the ako paradigm without changing manual annotations.

Highlights feature conflicts and unusual forms for review. Does not
assume a morpheme analysis for inago/egore/cenagore.
"""
from collections import Counter,defaultdict
from pathlib import Path
import argparse,csv

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--corpus",default="CorBo/Corpus_Files/CorBo.conllu")
    p.add_argument("--out",default="reports/tokenizer-v2/ako-audit.tsv")
    a=p.parse_args()
    rows=defaultdict(Counter)
    ids=defaultdict(list)
    sid=""
    for line in Path(a.corpus).open(encoding="utf-8-sig"):
        if line.startswith("# sent_id ="):sid=line.partition("=")[2].strip()
        elif not line.strip():sid=""
        elif not line.startswith("#"):
            c=line.rstrip("\n").split("\t")
            if len(c)!=10 or not c[0].isdigit() or c[2].casefold()!="ako":continue
            key=(c[1].casefold(),c[3],c[5])
            rows[c[1].casefold()][(c[3],c[5])]+=1
            if sid and sid not in ids[key] and len(ids[key])<5:ids[key].append(sid)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,delimiter="\t")
        w.writerow(["form","upos","feats","tokens","review_reason","sent_ids"])
        for form,analyses in sorted(rows.items(),key=lambda x:-sum(x[1].values())):
            total=sum(analyses.values())
            for (upos,feats),n in analyses.most_common():
                reasons=[]
                if upos not in ("VERB","AUX"):reasons.append("nonverbal_upos")
                if upos=="_":reasons.append("missing_upos")
                if feats=="_":reasons.append("missing_feats")
                if form in ("inago","inagore","inagokare") and "Person=3" in feats:reasons.append("person_conflict_check")
                if form in ("ego","egore") and "Number=Sing" in feats:reasons.append("number_conflict_check")
                if form in ("boe","oino","tagago"):reasons.append("unexpected_form_check")
                if n<=2:reasons.append("rare_analysis_check")
                w.writerow([form,upos,feats,n,";".join(reasons),",".join(ids.get((form,upos,feats),[]))])
    print(f"{len(rows)} casefolded forms; {sum(sum(c.values()) for c in rows.values())} tokens -> {out}")
    print("Review flags are hypotheses, not corrections; source annotations unchanged.")

if __name__=="__main__":main()
