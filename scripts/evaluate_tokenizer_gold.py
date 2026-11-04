#!/usr/bin/env python3
"""Evaluate CorBo morphological segmentation against independently reviewed gold.

Gold TSV columns: form, surface_segments, decision, split, note
- surface_segments: '+'-separated surface spans (e.g. i+re).
- decision: confirmed | ambiguous | unresolved | reject
- split: train | test (only test is scored)
- For ambiguous entries, multiple rows per form represent acceptable analyses.
- Unresolved entries are never scored.
- Reject entries are negative examples: the candidate segmentation must not match.
Do not use the model's own candidate analyses to create gold.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

FIELDS = ["form", "surface_segments", "decision", "split", "note"]
DECISIONS = {"confirmed", "ambiguous", "unresolved", "reject"}


def read_gold(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError("Gold TSV must contain: " + ", ".join(FIELDS))
        records = list(reader)
    grouped = defaultdict(list)
    for line, row in enumerate(records, 2):
        form = row["form"].strip().casefold()
        decision = row["decision"].strip().casefold()
        split = row["split"].strip().casefold()
        parts = tuple(x.strip().casefold() for x in row["surface_segments"].split("+")) if row["surface_segments"].strip() else ()
        if not form or decision not in DECISIONS or split not in {"train", "test"}:
            raise ValueError(f"Invalid gold entry at line {line}")
        if decision != "unresolved" and (not parts or any(not x for x in parts) or "".join(parts) != form):
            raise ValueError(f"Invalid surface segmentation at line {line}: {form}")
        grouped[form].append((decision, split, parts))
    for form, entries in grouped.items():
        if len({split for _, split, _ in entries}) != 1:
            raise ValueError(f"Form occurs in train and test: {form}")
        if len({decision for decision, _, _ in entries}) != 1:
            raise ValueError(f"Conflicting decisions: {form}")
        if len(entries) > 1 and entries[0][0] != "ambiguous":
            raise ValueError(f"Multiple gold entries require ambiguous decision: {form}")
    return grouped


def evaluate(model, gold):
    candidates = model.get("candidates", {})
    results = []
    counts = defaultdict(int)
    for form, entries in sorted(gold.items()):
        decision, split, _ = entries[0]
        if split != "test" or decision == "unresolved":
            continue
        allowed = {parts for _, _, parts in entries}
        cand = candidates.get(form)
        predicted = tuple(cand.get("segments", [])) if cand else ()
        predicted_nontrivial = bool(predicted and len(predicted) > 1)
        if decision == "reject":
            # Reject records represent explicitly rejected analyses, not
            # necessarily a claim that the word is morphologically atomic.
            outcome = "false_positive" if predicted in allowed else "correct_rejection"
        elif not predicted_nontrivial:
            outcome = "abstained"
        elif predicted in allowed:
            outcome = "correct"
        else:
            outcome = "incorrect"
        counts[outcome] += 1
        counts["evaluated"] += 1
        results.append({"form": form, "decision": decision, "gold": " | ".join("+".join(p) for p in sorted(allowed)), "predicted": "+".join(predicted), "candidate_status": cand.get("status", "") if cand else "", "outcome": outcome})
    positive = counts["correct"] + counts["incorrect"]
    counts["precision_on_predicted_positive_cases"] = round(counts["correct"] / positive, 4) if positive else None
    counts["coverage_on_test_cases"] = round((counts["correct"] + counts["incorrect"] + counts["false_positive"]) / counts["evaluated"], 4) if counts["evaluated"] else None
    return dict(counts), results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path("docs/data/tokenizer-model.json"))
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("tokenizer_gold_evaluation.json"))
    parser.add_argument("--details", type=Path, default=Path("tokenizer_gold_evaluation.csv"))
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    gold = read_gold(args.gold)
    scores, rows = evaluate(model, gold)
    report = {"model": str(args.model), "gold": str(args.gold), "test_forms": scores.get("evaluated", 0), "scores": scores, "caveats": ["Gold must be annotated independently of model proposals.", "Scores are exact surface-segmentation matches; no claim about morpheme gloss accuracy.", "Abstentions and rejected analyses are reported separately.", "Model training may already contain these surface forms; this is not a held-out-form evaluation unless trained with --exclude-forms."]}
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with args.details.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["form", "decision", "gold", "predicted", "candidate_status", "outcome"])
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
