#!/usr/bin/env python3
"""Atualiza índices morfológicos derivados de um CoNLL-U sem alterar a fonte."""
import argparse
import json
from pathlib import Path
from build_morph_integrated_index import build

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/"CorBo/Corpus_Files/corbo_fix(20261018-230729).conllu"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--corpus",type=Path,default=DEFAULT)
    p.add_argument("--output",type=Path,default=ROOT/"docs/data/morph-integrated-index.json")
    args=p.parse_args()
    if not args.corpus.is_file():
        p.error(f"Arquivo não encontrado: {args.corpus}")
    build(args.corpus,args.output)
    data=json.loads(args.output.read_text(encoding="utf-8"))
    print("Fonte:",args.corpus)
    print("Estatísticas:",json.dumps(data["stats"],ensure_ascii=False))
    print("CoNLL-U original preservado.")
if __name__=="__main__":
    main()
