#!/usr/bin/env python3
"""Summarize surface alternation candidates by lemma and evidence class.

This is a REVIEW report. It does not turn unresolved alignments into
morphological rules or claim segment-boundary accuracy.
"""
import argparse,csv,json
from collections import Counter,defaultdict
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="reports/tokenizer-v2/alternations.tsv")
    p.add_argument("--out",default="reports/tokenizer-v2/alternation-summary.json")
    a=p.parse_args()
    with Path(a.input).open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f,delimiter="\t"))
    groups=defaultdict(lambda:{"types":set(),"tokens":0,"examples":[]})
    by_status=Counter()
    for r in rows:
        status=r["alignment_status"]
        n=int(r["frequency"])
        by_status[status]+=n
        key=(r["lemma"],status)
        group=groups[key]
        group["types"].add(r["form"])
        group["tokens"]+=n
        if len(group["examples"])<8:
            group["examples"].append({
                "form":r["form"],"prefix":r["prefix_candidate"],
                "surface_base":r["surface_base_candidate"],
                "ending":r["ending_candidate"],
                "feats":r["feats"],"frequency":n})
    results=[
        {"lemma":lemma,"status":status,"types":len(g["types"]),
         "tokens":g["tokens"],"examples":g["examples"]}
        for (lemma,status),g in groups.items()
    ]
    results.sort(key=lambda x:(x["status"]!="unresolved",-x["tokens"],x["lemma"]))
    output={"source":a.input,"annotation_rows":len(rows),
            "tokens_by_alignment_status":dict(by_status),
            "lemma_status_groups":results,
            "warning":"Unresolved is not evidence of a morphological alternation; manual verification required."}
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"{len(rows)} annotation rows; {len(results)} lemma/status groups -> {path}")
    print("Token counts by alignment status:",dict(by_status))
    print("Highest-frequency unresolved lemma groups:")
    for item in [x for x in results if x["status"]=="unresolved"][:15]:
        print(item["lemma"],item["types"],item["tokens"])

if __name__=="__main__":main()
