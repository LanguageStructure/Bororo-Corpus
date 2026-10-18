#!/usr/bin/env python3
"""Audit initial-consonant rules against CorBo CoNLL-U.

Run: python3 scripts/audit_initial_alternations.py
Output: reports/morphology_global/initial_alternations_audit.csv
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bororo_initial_alternations import find_attested_analysis
from train_tokenizer import SOURCE, read_conllu, train

OUT = ROOT / "reports/morphology_global/initial_alternations_audit.csv"


def audit(rows):
    rows = list(rows)
    counts = Counter((form, lemma) for form, lemma, _ in rows if lemma)
    model = train(rows)
    results = []
    for (surface, lemma), frequency in sorted(counts.items()):
        match = find_attested_analysis(surface, lemma)
        if not match:
            continue
        selected = model["candidates"].get(surface, {})
        results.append({
            "surface": surface,
            "lemma": lemma,
            "frequency": frequency,
            "alternation": match["alternation"],
            "proposed_segments": "+".join(match["segments"]),
            "selected_segments": "+".join(selected.get("segments", [])),
            "selected_status": selected.get("status", "not_selected"),
            "agrees_with_selected": int(selected.get("segments") == match["segments"]),
            "review_status": "rule_candidate_not_individually_reviewed",
        })
    return results


def main():
    if not SOURCE.is_file():
        raise SystemExit("Missing source: " + str(SOURCE))
    results = audit(read_conllu(SOURCE))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["surface", "lemma", "frequency", "alternation",
              "proposed_segments", "selected_segments", "selected_status",
              "agrees_with_selected", "review_status"]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    by_rule = Counter(item["alternation"] for item in results)
    print("Rule-matched form/lemma pairs:", len(results))
    print("Rule-matched tokens:", sum(item["frequency"] for item in results))
    print("Agreement with selected segmentation:",
          sum(item["agrees_with_selected"] for item in results))
    for rule, count in sorted(by_rule.items()):
        print(rule, count)
    print("Review CSV:", OUT)


if __name__ == "__main__":
    main()
