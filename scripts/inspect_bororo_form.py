#!/usr/bin/env python3
"""Inspect a Bororo form across corpus annotations, dictionary, and rules.

No guessed segmentation is presented as confirmed. Dictionary records are
optional and retain their own provenance.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from train_tokenizer import SOURCE, read_conllu, train
from query_dictionary_paradigms import DEFAULT as DICTIONARY, build_index, query


def inspect(form, rows, dictionary_data=None):
    occurrences = [(lemma, upos) for surface, lemma, upos in rows if surface == form]
    model = train(rows)
    candidate = model["candidates"].get(form)
    dictionary_hits = query(build_index(dictionary_data), form) if dictionary_data else []
    return {
        "form": form,
        "corpus": {
            "occurrences": len(occurrences),
            "lemma_upos_counts": [
                {"lemma": lemma, "upos": upos, "count": occurrences.count((lemma, upos))}
                for lemma, upos in sorted(set(occurrences))
            ],
        },
        "tokenizer": candidate,
        "dictionary": {
            "available": dictionary_data is not None,
            "matches": dictionary_hits,
        },
        "evidence_policy": {
            "dictionary_unreviewed_is_not_gold": True,
            "tokenizer_rule_proposal_is_not_linguist_confirmation": True,
            "dictionary_absence_does_not_mean_lexical_absence": True,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("form")
    parser.add_argument("--corpus", type=Path, default=SOURCE)
    parser.add_argument("--dictionary", type=Path, default=DICTIONARY)
    args = parser.parse_args()
    if not args.corpus.is_file():
        parser.error("Corpus not found: " + str(args.corpus))
    dictionary_data = None
    if args.dictionary.is_file():
        dictionary_data = json.loads(args.dictionary.read_text(encoding="utf-8"))
    result = inspect(args.form, list(read_conllu(args.corpus)), dictionary_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
