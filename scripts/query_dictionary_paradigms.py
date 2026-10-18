#!/usr/bin/env python3
"""Query dictionary paradigm evidence without treating OCR as gold morphology.

Usage: python3 scripts/query_dictionary_paradigms.py FORM [--data FILE]
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "CorBo_vNext/annotations/dictionary_paradigms_candidates.json"


def build_index(data):
    index = defaultdict(list)
    for paradigm in data.get("paradigms", []):
        for entry in paradigm.get("entries", []):
            form = entry.get("working_form", "").strip()
            if not form:
                continue
            index[form].append({
                "form": form,
                "paradigm_id": paradigm["id"],
                "page": paradigm.get("pdf_page"),
                "column": paradigm.get("column"),
                "person_candidate": entry.get("person_candidate"),
                "reference_3sg_candidate": paradigm.get("reference_3sg_candidate"),
                "original": entry.get("original"),
                "entry_status": entry.get("status"),
                "flags": entry.get("flags"),
                "source": "dictionary_paradigm",
                "review_status": "unreviewed",
                "segmentation": None,
            })
    return index


def query(index, form):
    return list(index.get(form, []))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("form")
    parser.add_argument("--data", type=Path, default=DEFAULT)
    args = parser.parse_args()
    if not args.data.is_file():
        parser.error("Dictionary data missing: " + str(args.data))
    data = json.loads(args.data.read_text(encoding="utf-8"))
    print(json.dumps({
        "query": args.form,
        "matches": query(build_index(data), args.form),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
