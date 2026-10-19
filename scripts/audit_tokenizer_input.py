#!/usr/bin/env python3
"""Audit token inclusion and malformed FEATS without changing annotations.

Usage: python3 scripts/audit_tokenizer_input.py [path/to/file.conllu]
"""
from collections import Counter
from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
REPORT = ROOT / "reports/morphology_global/tokenizer_input_exclusions.csv"
FEATS_REPORT = ROOT / "reports/morphology_global/malformed_feats.csv"


def inspect(path):
    counts = Counter()
    exclusions = []
    malformed = []
    sent_id = ""
    with path.open(encoding="utf-8-sig") as handle:
        for lineno, raw in enumerate(handle, 1):
            line = raw.rstrip("\r\n")
            if line.startswith("# sent_id ="):
                sent_id = line.split("=", 1)[1].strip()
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) != 10:
                counts["invalid_column_count"] += 1
                exclusions.append((lineno, sent_id, cols[0], "invalid_column_count", ""))
                continue
            ident, form, lemma, upos, _, feats = cols[:6]
            if "-" in ident:
                counts["multiword_token_ranges"] += 1
                continue
            if "." in ident:
                counts["empty_nodes"] += 1
                continue
            if not ident.isdigit():
                counts["non_integer_ids"] += 1
                exclusions.append((lineno, sent_id, ident, "non_integer_id", form))
                continue
            counts["integer_id_rows"] += 1
            if not form or form == "_":
                counts["missing_form"] += 1
                exclusions.append((lineno, sent_id, ident, "missing_form", form))
                continue
            counts["tokenizer_included"] += 1
            if feats != "_" and not all(
                "=" in part and part.split("=", 1)[0] and part.split("=", 1)[1]
                for part in feats.split("|")
            ):
                counts["malformed_feats"] += 1
                malformed.append((lineno, sent_id, ident, form, feats))
    return counts, exclusions, malformed


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)


def main():
    source = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT
    if not source.is_file():
        raise SystemExit("Missing CoNLL-U: " + str(source))
    counts, exclusions, malformed = inspect(source)
    write_csv(REPORT, ("line", "sent_id", "id", "reason", "form"), exclusions)
    write_csv(FEATS_REPORT, ("line", "sent_id", "id", "form", "feats"), malformed)
    for key, value in sorted(counts.items()):
        print(f"{key}: {value}")
    print("Excluded token rows:", len(exclusions))
    print("Exclusions:", REPORT)
    print("Malformed FEATS:", FEATS_REPORT)
    print("No CoNLL-U annotations were changed.")


if __name__ == "__main__":
    main()
