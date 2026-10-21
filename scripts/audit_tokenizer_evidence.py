#!/usr/bin/env python3
"""Audit attested CoNLL-U forms without inventing morphological analyses.

Outputs a CSV of real tokens with missing lemma/UPOS and their source sent_id.
This is a review queue, not an automatic annotation or corpus correction.
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def collect(paths):
    records = defaultdict(lambda: {"count": 0, "missing_lemma": 0,
                                   "missing_upos": 0, "examples": []})
    for path in paths:
        sent_id = ""
        for line in path.open(encoding="utf-8-sig"):
            line = line.rstrip("\n")
            if not line:
                sent_id = ""
                continue
            if line.startswith("# sent_id ="):
                sent_id = line.split("=", 1)[1].strip()
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) != 10 or not cols[0].isdigit():
                continue  # Ignore multiword tokens and empty nodes.
            form, lemma, upos = cols[1:4]
            if form == "_":
                continue
            key = (str(path), form.casefold())
            rec = records[key]
            rec["count"] += 1
            rec["missing_lemma"] += lemma in ("", "_")
            rec["missing_upos"] += upos in ("", "_")
            if len(rec["examples"]) < 5 and (lemma in ("", "_") or upos in ("", "_")):
                rec["examples"].append(sent_id or "(missing sent_id)")
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="*", type=Path,
                        help="CoNLL-U files (default: CorBo/Corpus_Files/CorBo.conllu)")
    parser.add_argument("--output", type=Path, default=ROOT / "tokenizer_annotation_audit.csv")
    args = parser.parse_args()
    paths = args.sources or [ROOT / "CorBo/Corpus_Files/CorBo.conllu"]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        parser.error("Missing source files: " + ", ".join(missing))
    rows = collect(paths)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "form", "tokens", "missing_lemma",
                         "missing_upos", "example_sent_ids"])
        for (source, form), rec in sorted(rows.items(),
                                         key=lambda x: (-x[1]["missing_lemma"]-x[1]["missing_upos"],
                                                        -x[1]["count"], x[0])):
            if not (rec["missing_lemma"] or rec["missing_upos"]):
                continue
            writer.writerow([source, form, rec["count"], rec["missing_lemma"],
                             rec["missing_upos"], "; ".join(rec["examples"])])
    print(f"Audited {len(rows)} source/form pairs; wrote {args.output}")


if __name__ == "__main__":
    main()
