#!/usr/bin/env python3
"""Inspect exact-match errors against manually approved segmentations."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def boundaries(parts):
    positions = set()
    offset = 0
    for part in parts[:-1]:
        offset += len(part)
        positions.add(offset)
    return positions


def classify(expected, predicted):
    if predicted is None:
        return "unanalysed"
    if expected == predicted:
        return "correct"
    expected_bounds = boundaries(expected)
    predicted_bounds = boundaries(predicted)
    if not expected_bounds and predicted_bounds:
        return "oversegmentation"
    if expected_bounds and not predicted_bounds:
        return "undersegmentation"
    if predicted_bounds - expected_bounds and expected_bounds - predicted_bounds:
        return "mixed_boundary_error"
    if predicted_bounds - expected_bounds:
        return "oversegmentation"
    if expected_bounds - predicted_bounds:
        return "undersegmentation"
    return "other_mismatch"


def report(model, gold):
    candidates = model["candidates"]
    rows = []
    for item in gold:
        form = item["form"].casefold()
        expected = [x.casefold() for x in item["segments"]]
        if not expected or "".join(expected) != form:
            raise ValueError("Invalid gold segmentation: " + form)
        candidate = candidates.get(form)
        predicted = candidate["segments"] if candidate else None
        label = classify(expected, predicted)
        rows.append({
            "form": form,
            "expected": " + ".join(expected),
            "predicted": " + ".join(predicted) if predicted else "",
            "error_type": label,
            "prediction_status": candidate.get("status", "") if candidate else "",
            "gold_boundaries": ",".join(map(str, sorted(boundaries(expected)))),
            "predicted_boundaries": ",".join(map(str, sorted(boundaries(predicted)))) if predicted else "",
        })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "docs/data/tokenizer-model.json")
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "tokenizer_error_report.csv")
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    gold = json.loads(args.gold.read_text(encoding="utf-8"))
    rows = report(model, gold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "form", "expected", "predicted", "error_type", "prediction_status",
            "gold_boundaries", "predicted_boundaries"])
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(row["error_type"] for row in rows)
    print(json.dumps({"evaluated": len(rows), "error_categories": dict(sorted(counts.items())),
                      "output": str(args.output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
