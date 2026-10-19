#!/usr/bin/env python3
"""Display evidence for the highest-priority unsegmented forms, without guessing parses."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs/data/morphology-evidence.json"
QUEUE = ROOT / "reports/morphology_global/tokenizer_review_queue.csv"

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    if n < 1:
        raise SystemExit("Count must be positive")
    with QUEUE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))[:n]
    data = json.loads(INDEX.read_text(encoding="utf-8"))["forms"]
    for row in rows:
        form = row["form"]
        evidence = data[form]
        print(f"\n{form} | corpus tokens: {row['corpus_frequency']}")
        for analysis in sorted(evidence.get("corpus_analyses", []),
                               key=lambda a: -a.get("frequency", 0)):
            print("  corpus:", analysis.get("lemma", ""), analysis.get("upos", ""),
                  "n=", analysis.get("frequency", 0))
        for match in evidence.get("dictionary_matches", []):
            print("  dictionary:", "paradigm=", match.get("paradigm_id", ""),
                  "person=", match.get("person_candidate", ""),
                  "3sg_reference=", match.get("reference_3sg_candidate", ""),
                  "page=", match.get("page", ""),
                  "status=", match.get("review_status", "unreviewed"))
        print("  segmentation: UNREVIEWED; no segmentation proposed")
if __name__ == "__main__":
    main()
