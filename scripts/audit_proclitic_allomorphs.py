#!/usr/bin/env python3
"""Find corpus-wide candidates resembling reviewed proclitic allomorphs.

A surface match is not a morphological analysis. Output is review-only.
"""
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

# Reviewed aimo data motivate these searches, but do not prove productivity.
ONSET_CANDIDATES = {
    "1SG": ("it",), "2SG": ("ak",), "1PL.EX": ("ced",),
    "1PL.IN": ("pad",), "2PL": ("tag",),
}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("conllu", nargs="?", default="CorBo/Corpus_Files/CorBo.conllu")
    ap.add_argument("--output", default="reports/morphology_global/proclitic_allomorph_candidates.csv")
    args = ap.parse_args()
    source, target = Path(args.conllu), Path(args.output)
    if not source.is_file():
        ap.error("File not found: " + str(source))
    observations = Counter()
    ids = defaultdict(set)
    sid = ""
    for raw in source.open(encoding="utf-8"):
        line = raw.rstrip("\r\n")
        if line.startswith("# sent_id = "):
            sid = line.partition("=")[2].strip()
            continue
        cols = line.split("\t")
        if len(cols) != 10 or not cols[0].isdigit():
            continue
        form, lemma, upos, feats = cols[1:4] + [cols[5]]
        form, lemma = form.casefold(), lemma.casefold()
        if not form or lemma in ("", "_") or not lemma[0] in "aeiou":
            continue
        for person, prefixes in ONSET_CANDIDATES.items():
            for prefix in prefixes:
                if form == prefix + lemma:
                    key = (person, prefix, lemma, form, upos, feats)
                    observations[key] += 1
                    if sid and len(ids[key]) < 3:
                        ids[key].add(sid)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(("person_candidate", "prefix_candidate", "lemma", "form",
                         "upos", "feats", "frequency", "sent_ids", "status"))
        for key, count in sorted(observations.items(), key=lambda x: (-x[1], x[0])):
            writer.writerow((*key, count, ";".join(sorted(ids[key])),
                             "orthographic_candidate_review_required"))
    print("Candidate form/lemma/FEATS combinations:", len(observations))
    print("Distinct lemmas:", len({key[2] for key in observations}))
    print("Output:", target)

if __name__ == "__main__":
    main()
