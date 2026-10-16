#!/usr/bin/env python3
"""Produce an evidence table for competing analyses of ako forms.

Candidates are deliberately unconfirmed; do not use this report as gold
segmentation or to train productive allomorph rules.
"""
import argparse,csv
from collections import Counter,defaultdict
from pathlib import Path

HYPOTHESES={
 "inagore":[("i(n)+ago+re","confirmed_prefix_allomorph")],
 "inago":[("i(n)+ago","confirmed_prefix_allomorph")],
 "inagokare":[("i(n)+ago+ka+re","confirmed_prefix_allomorph")],
 "inagoi":[("i(n)+ago+i","prefix_confirmed_suffix_requires_review")],
 "cenagore":[("ce(n)+ago+re","confirmed_prefix_allomorph")],
 "inagorire":[("i(n)+ago+ri+re","prefix_confirmed_suffix_requires_review")],
 "egore":[("e+go+re","confirmed_prefix_and_base")],
 "ego":[("e+go","confirmed_prefix_and_base")],
 "akore":[("ako+re","attested_base_plus_indicative")],
 "ako":[("ako","unsegmented_base")],
 "akomode":[("ako+modu+re","irrealis_plus_indicative_candidate")],
 "egowo":[("e+go+wo","go_allomorph_subjunctive_candidate"),("ego+wo","ego_allomorph_subjunctive_candidate")],
 "egomodukare":[("e+go+modu+ka+re","go_allomorph_irrealis_negative_candidate"),("ego+modu+ka+re","ego_allomorph_irrealis_negative_candidate")],
}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--corpus",default="CorBo/Corpus_Files/CorBo.conllu")
 p.add_argument("--out",default="reports/tokenizer-v2/ako-hypotheses.tsv")
 a=p.parse_args()
 counts=Counter();sids=defaultdict(list);sid=""
 with Path(a.corpus).open(encoding="utf-8-sig") as f:
  for line in f:
   if line.startswith("# sent_id ="):sid=line.partition("=")[2].strip()
   elif not line.strip():sid=""
   elif not line.startswith("#"):
    c=line.rstrip("\n").split("\t")
    if len(c)!=10 or not c[0].isdigit() or c[2].casefold()!="ako":continue
    form=c[1].casefold();key=(form,c[3],c[5])
    counts[key]+=1
    if sid and sid not in sids[key] and len(sids[key])<5:sids[key].append(sid)
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
 with out.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f,delimiter="\t")
  w.writerow(["form","upos","feats","frequency","candidate","hypothesis","status","sent_ids"])
  for (form,upos,feats),n in counts.most_common():
   options=HYPOTHESES.get(form,[("","no_hypothesis")])
   for candidate,hypothesis in options:
    w.writerow([form,upos,feats,n,candidate,hypothesis,
                "confirmed_by_linguist" if hypothesis in ("confirmed_prefix_allomorph","confirmed_prefix_and_base") else "review_required" if len(options)>1 or not candidate or "requires_review" in hypothesis or "candidate" in hypothesis else "documented_candidate",
                ",".join(sids[(form,upos,feats)])])
 print(f"{len(counts)} annotated combinations; {sum(counts.values())} tokens -> {out}")
 print("Competing segmentations are hypotheses only. No corpus files modified.")
if __name__=="__main__":main()
