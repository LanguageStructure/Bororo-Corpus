#!/usr/bin/env python3
"""Import extracted dictionary paradigms as *unreviewed* lexical evidence.

Usage:
 python3 scripts/import_dictionary_paradigms.py /path/to/paradigmas_bororo_revisao.csv

Only full eight-slot paradigms receive a tentative third-person reference.
Never automatically license segmentations or infer UPOS from this source.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "CorBo_vNext/annotations/dictionary_paradigms_candidates.json"
SLOTS = ("1SG", "2SG", "3SG", "1PL.EX", "1PL.IN", "2PL", "3PL", "3REFL")


def build(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["id"]].append(row)
    paradigms = []
    for ident, group in sorted(groups.items()):
        group.sort(key=lambda r: int(r["position"]))
        complete = len(group) == 8 and [int(r["position"]) for r in group] == list(range(1, 9))
        entries = []
        for row in group:
            position = int(row["position"])
            entries.append({
                "position": position,
                "person_candidate": SLOTS[position - 1] if complete else None,
                "original": row["original"],
                "working_form": row["working_form"],
                "status": row["status"],
                "flags": row["flags"],
            })
        paradigms.append({
            "id": ident, "pdf_page": group[0]["pdf_page"],
            "column": group[0]["column"], "complete": complete,
            "reference_3sg_candidate": entries[2]["working_form"] if complete else None,
            "reference_status": "tentative_not_lexically_confirmed" if complete else "unavailable",
            "entries": entries,
        })
    return {
        "schema": "corbo-dictionary-paradigms-candidates/v1",
        "source": "extracted_dictionary_review_csv",
        "status": "unreviewed_do_not_train_as_gold",
        "slot_alignment": "tentative_for_complete_eight_form_paradigms_only",
        "paradigms": paradigms,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    with args.csv_path.open(encoding="utf-8-sig", newline="") as f:
        result = build(csv.DictReader(f))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Paradigms:", len(result["paradigms"]))
    print("Complete:", sum(p["complete"] for p in result["paradigms"]))
    print("Forms:", sum(len(p["entries"]) for p in result["paradigms"]))
    print("Output:", OUT)


if __name__ == "__main__":
    main()
