#!/usr/bin/env python3
"""Audit proposed root-initial consonant alternations across attested verb forms.

Exploratory only: matching a prefix and a consonant pair does NOT validate segmentation.
"""
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

PAIRS = (("k", "g"), ("t", "d"), ("b", "w"), ("p", "b"), ("c", "j"))
PREFIXES = ("ce", "pa", "ta", "tu", "i", "a", "u", "e")

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("conllu", nargs="?", default="CorBo/Corpus_Files/CorBo.conllu")
    ap.add_argument("--output", default="reports/morphology_global/initial_alternations_review.csv")
    args = ap.parse_args()
    src, dst = Path(args.conllu), Path(args.output)
    if not src.is_file():
        ap.error("CoNLL-U not found: " + str(src))
    counts = Counter()
    examples = defaultdict(set)
    sent_id = ""
    for raw in src.open(encoding="utf-8"):
        line = raw.rstrip("\r\n")
        if line.startswith("# sent_id = "):
            sent_id = line.partition("=")[2].strip()
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 10 or not cols[0].isdigit() or cols[3] != "VERB":
            continue
        form, lemma = cols[1].lower(), cols[2].lower()
        if lemma == "_" or form == "_":
            continue
        counts[(lemma, form)] += 1
        if sent_id and len(examples[(lemma, form)]) < 3:
            examples[(lemma, form)].add(sent_id)
    rows = []
    for (lemma, form), n in counts.items():
        for prefix in PREFIXES:
            if not form.startswith(prefix) or len(form) <= len(prefix):
                continue
            remainder = form[len(prefix):]
            for a, b in PAIRS:
                if lemma.startswith(a) and remainder.startswith(b) and lemma[1:] == remainder[1:]:
                    rows.append((lemma, form, prefix, a, b, n, counts.get((lemma, lemma), 0),
                                 ";".join(sorted(examples[(lemma, form)])),
                                 "candidate_requires_manual_review"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(("lemma", "attested_form", "prefix_candidate", "lemma_initial",
                         "surface_initial", "form_count", "bare_lemma_form_count",
                         "example_sent_ids", "status"))
        writer.writerows(sorted(rows))
    print("Candidate lemma/form alternations:", len(rows))
    print("Distinct lemmas:", len({r[0] for r in rows}))
    print("Output:", dst)

if __name__ == "__main__":
    main()
