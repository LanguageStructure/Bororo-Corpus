#!/usr/bin/env python3
"""Atualiza o índice morfológico e mede cobertura sem alterar o CoNLL-U."""
import argparse
import json
from collections import Counter
from pathlib import Path
from build_morph_integrated_index import build

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/"CorBo/Corpus_Files/CorBo_20261027.conllu"

def coverage(entries):
    counts=Counter()
    for row in entries:
        freq=row["frequency"]
        analyses=row.get("morphological_segmentations",[])
        statuses={a.get("status") for a in analyses}
        confirmed=[a for a in analyses if a.get("status")=="confirmed"]
        if confirmed:
            group="confirmed_segmented" if any(len(a.get("segments",[]))>1 for a in confirmed) else "confirmed_atomic"
        elif "hypothesis" in statuses:
            group="hypothesis"
        else:
            group="unanalysed"
        counts[group+"_types"]+=1
        counts[group+"_tokens"]+=freq
        if row.get("lexical_evidence"):
            counts["lexical_types"]+=1
            counts["lexical_tokens"]+=freq
    total_types=len(entries)
    total_tokens=sum(row["frequency"] for row in entries)
    result={"total_types":total_types,"total_tokens":total_tokens}
    for group in ("confirmed_segmented","confirmed_atomic","hypothesis","unanalysed","lexical"):
        for unit,total in (("types",total_types),("tokens",total_tokens)):
            value=counts[group+"_"+unit]
            result[group+"_"+unit]=value
            result[group+"_"+unit+"_pct"]=round(100*value/total,2) if total else 0
    for unit,total in (("types",total_types),("tokens",total_tokens)):
        value=counts["confirmed_segmented_"+unit]+counts["confirmed_atomic_"+unit]
        result["confirmed_"+unit]=value
        result["confirmed_"+unit+"_pct"]=round(100*value/total,2) if total else 0
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--corpus",type=Path,default=DEFAULT)
    p.add_argument("--output",type=Path,default=ROOT/"docs/data/morph-integrated-index.json")
    p.add_argument("--report",type=Path,default=None,help="Salvar relatório JSON opcional")
    args=p.parse_args()
    if not args.corpus.is_file():
        p.error(f"Arquivo não encontrado: {args.corpus}")
    build(args.corpus,args.output)
    data=json.loads(args.output.read_text(encoding="utf-8"))
    report={"source":data["source"],"coverage":coverage(data["entries"])}
    print("Fonte:",args.corpus)
    print("Cobertura:",json.dumps(report["coverage"],ensure_ascii=False,indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("Relatório:",args.report)
    print("CoNLL-U original preservado.")

if __name__=="__main__":
    main()
