#!/usr/bin/env python3
"""Rank dictionary/corpus overlaps for manual tokenizer review.

No inferred morpheme boundaries are treated as validated segmentations.
Run after build_morphology_evidence.py.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/data/morphology-evidence.json"
OUT = ROOT / "reports/morphology_global/tokenizer_review_queue.csv"

def queue(data):
    result = []
    for form, evidence in data["forms"].items():
        if not evidence.get("corpus_frequency") or not evidence.get("dictionary_matches"):
            continue
        if (evidence.get("tokenizer") or {}).get("segments"):
            continue
        matches = evidence["dictionary_matches"]
        paradigms = sorted({str(x.get("paradigm_id", "")) for x in matches})
        people = sorted({str(x.get("person_candidate")) for x in matches if x.get("person_candidate")})
        lemmas = sorted({x.get("lemma", "") for x in evidence.get("corpus_analyses", []) if x.get("lemma")})
        result.append({
            "form": form,
            "corpus_frequency": evidence["corpus_frequency"],
            "paradigm_count": len(paradigms),
            "paradigms": "|".join(paradigms),
            "person_candidates": "|".join(people),
            "corpus_lemmas": "|".join(lemmas),
            "dictionary_pages": "|".join(sorted({str(x.get("page")) for x in matches if x.get("page")})),
            "proposed_segmentation": "",
            "review_status": "needs_linguist_review",
        })
    return sorted(result, key=lambda x: (-x["corpus_frequency"], -x["paradigm_count"], x["form"]))

def main():
    if not SOURCE.exists():
        raise SystemExit("Run python3 scripts/build_morphology_evidence.py first")
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = queue(data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["form", "corpus_frequency", "paradigm_count", "paradigms",
              "person_candidates", "corpus_lemmas", "dictionary_pages",
              "proposed_segmentation", "review_status"]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("Forms awaiting segmentation:", len(rows))
    print("Total attested tokens represented:", sum(r["corpus_frequency"] for r in rows))
    print("First 20 review forms:", ", ".join(r["form"] for r in rows[:20]))
    print("Review queue:", OUT)

if __name__ == "__main__":
    main()
