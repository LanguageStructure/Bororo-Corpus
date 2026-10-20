#!/usr/bin/env python3
"""Create a reproducible, UNANNOTATED stratified review sample.

Sampling does not establish gold analyses. The reviewer must fill segments
without consulting the tokenizer predictions. Keep this file out of training.
"""
import argparse
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sample(model, size=150, seed=20261020):
    lexicon = model["lexicon"]
    candidates = model["candidates"]
    strata = {"confirmed": [], "proposed": [], "unanalysed": []}
    for form, item in lexicon.items():
        candidate = candidates.get(form)
        label = ("confirmed" if candidate and candidate.get("status") == "linguistically_confirmed"
                 else "proposed" if candidate else "unanalysed")
        strata[label].append((form, item["frequency"]))
    rng = random.Random(seed)
    for values in strata.values():
        values.sort()
        rng.shuffle(values)
    labels = list(strata)
    selected = []
    quotas = {label: size // len(labels) for label in labels}
    for label in labels[:size % len(labels)]:
        quotas[label] += 1
    for label in labels:
        count = min(quotas[label], len(strata[label]))
        selected.extend((label, form, freq) for form, freq in strata[label][:count])
        strata[label] = strata[label][count:]
    remaining = size - len(selected)
    while remaining:
        available = [label for label in labels if strata[label]]
        if not available:
            break
        for label in available:
            if not remaining:
                break
            form, freq = strata[label].pop(0)
            selected.append((label, form, freq))
            remaining -= 1
    rng.shuffle(selected)
    return [{"form": form, "frequency": freq, "stratum": label,
             "segments": "", "review_status": "pending", "reviewer_note": ""}
            for label, form, freq in selected]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "docs/data/tokenizer-model.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tokenizer_gold_review.csv")
    parser.add_argument("--size", type=int, default=150)
    parser.add_argument("--seed", type=int, default=20261020)
    args = parser.parse_args()
    if args.size < 1:
        parser.error("--size must be positive")
    model = json.loads(args.model.read_text(encoding="utf-8"))
    rows = sample(model, args.size, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["form", "frequency", "stratum", "segments", "review_status", "reviewer_note"])
        writer.writeheader()
        writer.writerows(rows)
    print("Unannotated review sample:", len(rows), "->", args.output)
    print("Do not use sampled forms to develop rules before held-out evaluation.")


if __name__ == "__main__":
    main()
