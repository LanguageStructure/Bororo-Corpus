#!/usr/bin/env python3
"""Audit the overlap of corpus and extracted dictionary paradigms.

This report compares *evidence*, not independent gold segmentations:
dictionary entries currently have no reviewed morpheme boundaries.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/data/morphology-evidence.json"
OUT = ROOT / "reports/morphology_global/dictionary_corpus_overlap.csv"


def audit(data):
    results = []
    for form, item in sorted(data.get("forms", {}).items()):
        if not item.get("corpus_frequency") or not item.get("dictionary_matches"):
            continue
        candidate = item.get("tokenizer") or {}
        dictionary = item["dictionary_matches"]
        lemmas = sorted({a.get("lemma", "") for a in item.get("corpus_analyses", []) if a.get("lemma")})
        reference_forms = sorted({d.get("reference_3sg_candidate") for d in dictionary
                                  if d.get("reference_3sg_candidate")})
        candidate_lemma = candidate.get("lemma", "")
        # A 3SG paradigm reference is NOT automatically a lemma.
        results.append({
            "form": form,
            "corpus_frequency": item["corpus_frequency"],
            "corpus_lemmas": "|".join(lemmas),
            "dictionary_paradigms": "|".join(sorted({str(d.get("paradigm_id", "")) for d in dictionary})),
            "dictionary_reference_candidates": "|".join(reference_forms),
            "dictionary_person_candidates": "|".join(sorted({str(d.get("person_candidate"))
                                                               for d in dictionary if d.get("person_candidate")})),
            "tokenizer_segments": "+".join(candidate.get("segments", [])),
            "tokenizer_lemma": candidate_lemma,
            "tokenizer_status": candidate.get("status", "no_candidate"),
            "corpus_supports_tokenizer_lemma": (
                "yes" if candidate_lemma and candidate_lemma in lemmas else
                "no" if candidate_lemma else "not_applicable"
            ),
            "comparison_status": (
                "segmented_but_dictionary_unreviewed" if candidate.get("segments") else
                "no_segmentation_dictionary_unreviewed"
            ),
            "needs_review": "yes",
        })
    return results


def main():
    if not SOURCE.is_file():
        raise SystemExit("Index missing; run python3 scripts/build_morphology_evidence.py")
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = audit(data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["form", "corpus_frequency", "corpus_lemmas", "dictionary_paradigms",
              "dictionary_reference_candidates", "dictionary_person_candidates",
              "tokenizer_segments", "tokenizer_lemma", "tokenizer_status",
              "corpus_supports_tokenizer_lemma", "comparison_status", "needs_review"]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    by_status = Counter(row["tokenizer_status"] for row in rows)
    print("Shared forms:", len(rows))
    print("Shared forms with tokenizer segmentation:",
          sum(bool(row["tokenizer_segments"]) for row in rows))
    print("Shared forms without tokenizer segmentation:",
          sum(not row["tokenizer_segments"] for row in rows))
    print("Tokenizer statuses:", dict(sorted(by_status.items())))
    print("Independent dictionary segmentation comparisons: 0 (not annotated)")
    print("Review CSV:", OUT)


if __name__ == "__main__":
    main()
