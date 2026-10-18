#!/usr/bin/env python3
"""Build a static, provenance-aware morphology index for the CorBo website.

No dictionary-only entry is automatically assigned a morphological parse.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from train_tokenizer import SOURCE, read_conllu, train
from query_dictionary_paradigms import DEFAULT, build_index

OUT = ROOT / "docs/data/morphology-evidence.json"


def build(rows, dictionary=None):
    rows = list(rows)
    model = train(rows)
    forms = defaultdict(Counter)
    for surface, lemma, upos in rows:
        forms[surface][(lemma, upos)] += 1
    dictionary_index = build_index(dictionary) if dictionary else {}
    result = {}
    for form in sorted(set(forms) | set(dictionary_index)):
        analyses = forms.get(form, Counter())
        candidate = model["candidates"].get(form)
        result[form] = {
            "corpus_frequency": sum(analyses.values()),
            "corpus_analyses": [
                {"lemma": lemma, "upos": upos, "frequency": count}
                for (lemma, upos), count in sorted(analyses.items())
            ],
            "tokenizer": candidate,
            "dictionary_matches": dictionary_index.get(form, []),
            "dictionary_reviewed": False,
        }
    return {
        "schema": "corbo-morphology-evidence/v1",
        "sources": {
            "corpus": str(SOURCE.relative_to(ROOT)),
            "dictionary_loaded": dictionary is not None,
            "dictionary_status": "unreviewed",
        },
        "forms": result,
    }


def main():
    if not SOURCE.is_file():
        raise SystemExit("Corpus missing: " + str(SOURCE))
    dictionary = json.loads(DEFAULT.read_text(encoding="utf-8")) if DEFAULT.is_file() else None
    data = build(read_conllu(SOURCE), dictionary)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("Indexed forms:", len(data["forms"]))
    print("Forms with dictionary evidence:",
          sum(bool(item["dictionary_matches"]) for item in data["forms"].values()))
    print("Forms with tokenizer candidate:",
          sum(item["tokenizer"] is not None for item in data["forms"].values()))
    print("Dictionary loaded:", dictionary is not None)
    corpus_forms = {form for form, item in data["forms"].items()
                    if item["corpus_frequency"] > 0}
    dictionary_forms = {form for form, item in data["forms"].items()
                        if item["dictionary_matches"]}
    print("Corpus forms:", len(corpus_forms))
    print("Distinct dictionary forms:", len(dictionary_forms))
    print("Dictionary forms also in corpus:", len(dictionary_forms & corpus_forms))
    print("Dictionary-only forms:", len(dictionary_forms - corpus_forms))
    if dictionary is None:
        print("WARNING: dictionary file not found:", DEFAULT)
        print("The index is corpus-only. Supply the JSON and rebuild.")
    print("Output:", OUT)


if __name__ == "__main__":
    main()
