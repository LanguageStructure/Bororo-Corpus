#!/usr/bin/env python3
"""Conservative out-of-vocabulary analysis from attested lemma and affix patterns.

Output is always a proposal, never a linguist-confirmed analysis.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = ("ce", "pa", "ta", "tu", "i", "a", "u", "e")
ENDINGS = {
    "modukare": ["modu", "ka", "re"],
    "modure": ["modu", "re"],
    "kare": ["ka", "re"],
    "re": ["re"],
    "do": ["do"],
}


def analyze(form, model, min_lemma_frequency=3):
    form = form.casefold().strip()
    if not form or not form.isalpha():
        return []
    lexicon = model.get("lexicon", {})
    # Never claim a new analysis for an attested form.
    if form in lexicon:
        return []
    results = []
    seen = set()
    for prefix in ("", *PREFIXES):
        if prefix and not form.startswith(prefix):
            continue
        remainder = form[len(prefix):]
        for ending, suffix in [("", []), *ENDINGS.items()]:
            if ending and not remainder.endswith(ending):
                continue
            stem = remainder[:-len(ending)] if ending else remainder
            if len(stem) < 3 or stem not in lexicon:
                continue
            base = lexicon[stem]
            if base.get("frequency", 0) < min_lemma_frequency:
                continue
            # A stem observed as a surface form is not automatically its lemma.
            if not any(a.get("lemma") == stem for a in base.get("analyses", [])):
                continue
            if not prefix and not ending:
                continue
            pieces = ([prefix] if prefix else []) + [stem] + suffix
            if "".join(pieces) != form:
                continue
            key = tuple(pieces)
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "form": form,
                "segments": pieces,
                "lemma": stem,
                "status": "proposed",
                "evidence": "attested_independent_lemma_plus_surface_affixes",
                "warning": "Hypothesis only; affix combination and lexical compatibility not confirmed.",
            })
    return sorted(results, key=lambda x: (len(x["segments"]), x["segments"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("form")
    parser.add_argument("--model", type=Path, default=ROOT / "docs/data/tokenizer-model.json")
    parser.add_argument("--min-lemma-frequency", type=int, default=3)
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    print(json.dumps(analyze(args.form, model, args.min_lemma_frequency), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
