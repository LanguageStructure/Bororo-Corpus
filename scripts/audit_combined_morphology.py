#!/usr/bin/env python3
"""Audit combined prefix+allomorph+suffix coverage against CorBo CoNLL-U.

Usage: python3 scripts/audit_combined_morphology.py
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bororo_combined_morphology import analyze_combined
from train_tokenizer import SOURCE, read_conllu, train

OUTPUT = ROOT / "reports/morphology_global/combined_morphology_audit.csv"


def audit(rows):
    rows = list(rows)
    model = train(rows)
    counts = Counter((form, lemma) for form, lemma, _ in rows if lemma)
    results = []
    for (surface, lemma), frequency in sorted(counts.items()):
        proposed = analyze_combined(surface, lemma)
        if proposed is None:
            continue
        chosen = model["candidates"].get(surface, {})
        results.append({
            "surface": surface, "lemma": lemma, "frequency": frequency,
            "alternation": proposed["alternation"],
            "ending": proposed["segments"][-1],
            "proposed_segments": "+".join(proposed["segments"]),
            "selected_segments": "+".join(chosen.get("segments", [])),
            "selected_status": chosen.get("status", "not_selected"),
            "agrees_with_selected": int(chosen.get("segments") == proposed["segments"]),
            "review_status": "automated_candidate_not_linguist_confirmed",
        })
    return results


def main():
    if not SOURCE.is_file():
        raise SystemExit("Missing corpus: " + str(SOURCE))
    results = audit(read_conllu(SOURCE))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = ["surface", "lemma", "frequency", "alternation", "ending",
               "proposed_segments", "selected_segments", "selected_status",
               "agrees_with_selected", "review_status"]
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)
    print("Combined form/lemma pairs:", len(results))
    print("Combined tokens:", sum(row["frequency"] for row in results))
    print("Agreement with selected segmentation:",
          sum(row["agrees_with_selected"] for row in results))
    print("By alternation:", dict(sorted(Counter(row["alternation"] for row in results).items())))
    print("By final segment:", dict(sorted(Counter(row["ending"] for row in results).items())))
    print("Output:", OUTPUT)


if __name__ == "__main__":
    main()
