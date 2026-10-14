#!/usr/bin/env python3
"""Build a reproducible, conservative lexical model from CorBo CoNLL-U.

Usage: python3 scripts/train_tokenizer.py
Only public CoNLL-U columns FORM, LEMMA, UPOS are read. No review files.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUTPUT = ROOT / "docs/data/tokenizer-model.json"
PREFIXES = ("ce", "pa", "ta", "tu", "i", "a", "u", "e")
SUFFIXES = ("modukare", "modure", "re", "do")
MIN_SUPPORT = 3


def read_conllu(path):
    for line in path.open(encoding="utf-8-sig"):
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 4 or not cols[0].isdigit():
            continue
        form, lemma, upos = cols[1:4]
        if not form or form == "_":
            continue
        yield form.casefold(), lemma.casefold() if lemma != "_" else "", upos


def train(rows):
    forms = Counter()
    analyses = defaultdict(Counter)
    families = defaultdict(Counter)
    for form, lemma, upos in rows:
        forms[form] += 1
        analyses[form][(lemma, upos)] += 1
        if lemma:
            families[lemma][form] += 1
    # Observed grammatical units and their contiguous token sequences.
    # These are distributional statistics, not claims of internal morphology.
    grammatical = {"u", "nu", "re"}
    grammatical_counts = {unit: forms[unit] for unit in sorted(grammatical)}
    # Observed surface forms alone do not license a morphological boundary.
    # Candidate analyses must share a CoNLL-U lemma with an independently
    # attested base. Enumerate prefix+base+suffix as well as single affixes.
    # Surface segmentation candidates require evidence of a base attested
    # independently AND an identical lemma family; no b/w or k/g guessing.
    candidates = {}
    for form, n in forms.items():
        options = []
        related_lemmas = {lemma for lemma, _upos in analyses[form] if lemma}
        for lemma in related_lemmas:
            if form == lemma or lemma not in forms or len(lemma) < 3:
                continue
            support = families[lemma][form]
            for prefix in ("", *PREFIXES):
                for suffix in ("", *SUFFIXES):
                    if not prefix and not suffix:
                        continue
                    if form != prefix + lemma + suffix:
                        continue
                    pieces = ([prefix] if prefix else []) + [lemma]
                    if suffix:
                        pieces += ["modu", "ka", "re"] if suffix == "modukare" else ["modu", "re"] if suffix == "modure" else [suffix]
                    options.append((support, pieces))
        options = [(support, parts) for support, parts in options if support >= MIN_SUPPORT]
        if options:
            options.sort(key=lambda x: (-x[0], -len(x[1]), x[1]))
            candidates[form] = {"segments": options[0][1], "support": options[0][0], "status": "proposed"}
    # Discover recurring grammatical endings in lemma-linked forms.
    # Counts are evidence for candidate discovery, never confirmation.
    suffix_evidence = defaultdict(lambda: {"types": 0, "tokens": 0, "examples": []})
    for form, item in candidates.items():
        parts = item["segments"]
        for ending in ("re", "do", "modure", "modukare"):
            suffix_parts = {"re": ["re"], "do": ["do"], "modure": ["modu", "re"], "modukare": ["modu", "ka", "re"]}[ending]
            if parts[-len(suffix_parts):] == suffix_parts:
                record = suffix_evidence[ending]
                record["types"] += 1
                record["tokens"] += forms[form]
                if len(record["examples"]) < 8:
                    record["examples"].append(form)
    suffix_evidence = dict(sorted(suffix_evidence.items()))
    # Distributional discovery from recurring word endings, independent of
    # lemma annotations. This is evidence for investigation, not segmentation.
    ending_counts = defaultdict(lambda: {"types": 0, "tokens": 0, "examples": []})
    for form, freq in forms.items():
        if len(form) < 5 or not form.isalpha():
            continue
        for width in range(2, min(6, len(form) - 2) + 1):
            ending = form[-width:]
            record = ending_counts[ending]
            record["types"] += 1
            record["tokens"] += freq
            if len(record["examples"]) < 5:
                record["examples"].append(form)
    recurrent_endings = {
        ending: record for ending, record in sorted(ending_counts.items())
        if record["types"] >= 5 and record["tokens"] >= 20
    }
    return {
        "schema": "corbo-tokenizer-model/v1",
        "source": str(SOURCE.relative_to(ROOT)),
        "min_support": MIN_SUPPORT,
        "grammatical_unit_counts": grammatical_counts,
        "grammatical_unit_attested": {unit: bool(forms[unit]) for unit in sorted(grammatical)},
        "types": len(forms),
        "tokens": sum(forms.values()),
        "lexicon": {
            form: {
                "frequency": freq,
                "analyses": [
                    {"lemma": lemma, "upos": upos, "frequency": n}
                    for (lemma, upos), n in analyses[form].most_common()
                ],
            }
            for form, freq in sorted(forms.items())
        },
        "candidates": dict(sorted(candidates.items())),
        "suffix_evidence": suffix_evidence,
        "recurrent_endings": recurrent_endings,
    }


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing CoNLL-U: {SOURCE}")
    model = train(read_conllu(SOURCE))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(model, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{model['types']} types; {model['tokens']} tokens; {len(model['candidates'])} candidate segmentations -> {OUTPUT}")


if __name__ == "__main__":
    main()
