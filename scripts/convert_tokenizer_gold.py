#!/usr/bin/env python3
"""Validate manually reviewed CSV and export a gold JSON for evaluation."""
import argparse
import csv
import json
from pathlib import Path


def convert(rows, require_all=False):
    gold = []
    pending = []
    seen = set()
    for line, row in enumerate(rows, 2):
        form = (row.get("form") or "").strip().casefold()
        if not form:
            raise ValueError(f"Line {line}: missing form")
        if form in seen:
            raise ValueError(f"Line {line}: duplicate form {form}")
        seen.add(form)
        status = (row.get("review_status") or "").strip().casefold()
        if status != "approved":
            pending.append(form)
            continue
        raw = (row.get("segments") or "").strip()
        if not raw:
            raise ValueError(f"Line {line}: approved form without segmentation")
        # Use + between surface segments, e.g. ik + ie. Parenthetical
        # linguistic notation is not the surface form and is not accepted.
        segments = [part.strip().casefold() for part in raw.split("+")]
        if not all(segments) or "".join(segments) != form:
            raise ValueError(f"Line {line}: segments do not reconstruct {form}")
        gold.append({"form": form, "segments": segments})
    if require_all and pending:
        raise ValueError(f"{len(pending)} forms remain unapproved")
    return gold, pending


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-all", action="store_true")
    args = parser.parse_args()
    with args.csv_path.open(encoding="utf-8-sig", newline="") as file:
        gold, pending = convert(csv.DictReader(file), args.require_all)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(gold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Approved: {len(gold)}; pending: {len(pending)}; output: {args.output}")


if __name__ == "__main__":
    main()
