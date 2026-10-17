#!/usr/bin/env python3
"""Read-only inventory of attested mako inflections and FEATS conflicts.

Usage: python3 scripts/audit_mako_inflections.py [input.conllu] [output.csv]
Does not confirm morphological boundaries or change the tokenizer.
"""
import csv
import sys
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUTPUT = ROOT / "reports/mako_inflections.csv"
# Orthographic hypotheses only. Stem allomorphy must be checked manually.
ENDINGS = ("modukare", "kare", "mode", "nure", "re", "do", "i")


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    groups = defaultdict(lambda: {"feats": Counter(), "sent_ids": [], "upos": Counter()})
    sid = ""
    for line in source.open(encoding="utf-8-sig"):
        line = line.rstrip("\r\n")
        if not line:
            sid = ""
            continue
        if line.startswith("# sent_id ="):
            sid = line.partition("=")[2].strip()
            continue
        if line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 10 or not cols[0].isdigit() or cols[2].casefold() != "mako":
            continue
        form = cols[1].casefold()
        record = groups[form]
        record["feats"][cols[5]] += 1
        record["upos"][cols[3]] += 1
        if sid and sid not in record["sent_ids"] and len(record["sent_ids"]) < 8:
            record["sent_ids"].append(sid)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["form", "tokens", "ending_candidate", "feats_variants",
                         "upos", "example_sent_ids", "status"])
        for form, record in sorted(groups.items(), key=lambda pair: (-sum(pair[1]["feats"].values()), pair[0])):
            ending = next((x for x in ENDINGS if form.endswith(x)), "")
            writer.writerow([
                form, sum(record["feats"].values()), ending,
                "; ".join(f"{feat} ({n})" for feat, n in record["feats"].most_common()),
                "; ".join(f"{upos} ({n})" for upos, n in record["upos"].most_common()),
                "; ".join(record["sent_ids"]), "attested_requires_morphological_review",
            ])
    print(f"{len(groups)} formas de mako → {output}")
    print("Terminações são pistas ortográficas; nenhuma segmentação foi confirmada.")


if __name__ == "__main__":
    main()
