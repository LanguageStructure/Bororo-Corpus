#!/usr/bin/env python3
"""Measure coverage separately from segmentation accuracy."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def evaluate(model, gold=None):
    lexicon = model["lexicon"]
    candidates = model["candidates"]
    total_tokens = sum(x["frequency"] for x in lexicon.values())
    analysed = {f: x for f, x in lexicon.items() if f in candidates}
    confirmed = {f: x for f, x in analysed.items()
                 if candidates[f].get("status") == "linguistically_confirmed"}
    def ratio(n, d):
        return n / d if d else None
    report = {
        "schema": "corbo-tokenizer-evaluation/v1",
        "corpus_types": len(lexicon),
        "corpus_tokens": total_tokens,
        "analysed_types": len(analysed),
        "analysed_tokens": sum(x["frequency"] for x in analysed.values()),
        "confirmed_types": len(confirmed),
        "confirmed_tokens": sum(x["frequency"] for x in confirmed.values()),
        "type_coverage": ratio(len(analysed), len(lexicon)),
        "token_coverage": ratio(sum(x["frequency"] for x in analysed.values()), total_tokens),
        "confirmed_type_coverage": ratio(len(confirmed), len(lexicon)),
        "confirmed_token_coverage": ratio(sum(x["frequency"] for x in confirmed.values()), total_tokens),
        "gold_evaluation": None,
    }
    if gold is not None:
        correct = 0
        predicted = 0
        for item in gold:
            form = item["form"].casefold()
            segments = [s.casefold() for s in item["segments"]]
            if not segments or "".join(segments) != form:
                raise ValueError("Invalid gold segmentation: " + form)
            candidate = candidates.get(form)
            if candidate is not None:
                predicted += 1
                correct += candidate["segments"] == segments
        report["gold_evaluation"] = {
            "items": len(gold),
            "predicted": predicted,
            "correct_exact": correct,
            "exact_match_all": ratio(correct, len(gold)),
            "exact_match_predicted": ratio(correct, predicted),
            "note": "Independent accuracy only when gold was held out during development.",
        }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "docs/data/tokenizer-model.json")
    parser.add_argument("--gold", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    gold = json.loads(args.gold.read_text(encoding="utf-8")) if args.gold else None
    result = evaluate(model, gold)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
