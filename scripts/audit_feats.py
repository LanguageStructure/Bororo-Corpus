#!/usr/bin/env python3
"""Read-only audit of malformed CoNLL-U FEATS; never changes annotations.

Usage:
  python3 scripts/audit_feats.py [input.conllu] [output.csv]
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUTPUT = ROOT / "reports/feats_audit.csv"


def issues(raw):
    if raw == "_":
        return []
    problems = []
    for item in raw.split("|"):
        if not item:
            problems.append("empty_segment")
        elif "=" not in item:
            problems.append("missing_equals")
        else:
            key, value = item.split("=", 1)
            if not key:
                problems.append("empty_key")
            if not value:
                problems.append("empty_value")
    return sorted(set(problems))


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    if not source.is_file():
        raise SystemExit(f"Arquivo não encontrado: {source}")
    rows = []
    counts = Counter()
    sent_id = ""
    text = ""
    with source.open(encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.rstrip("\r\n")
            if not line:
                sent_id, text = "", ""
                continue
            if line.startswith("# sent_id ="):
                sent_id = line.partition("=")[2].strip()
                continue
            if line.startswith("# text ="):
                text = line.partition("=")[2].strip()
                continue
            if line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) != 10 or not fields[0].isdigit():
                continue
            problems = issues(fields[5])
            if not problems:
                continue
            counts.update(problems)
            rows.append({
                "line": line_no, "sent_id": sent_id, "token_id": fields[0],
                "form": fields[1], "lemma": fields[2], "upos": fields[3],
                "feats": fields[5], "issues": ";".join(problems), "text": text,
            })
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "line", "sent_id", "token_id", "form", "lemma", "upos",
            "feats", "issues", "text",
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} tokens com FEATS malformados → {output}")
    for name, count in sorted(counts.items()):
        print(f"  {name}: {count}")
    print("Categorias podem coexistir no mesmo token; totais não são aditivos.")


if __name__ == "__main__":
    main()
