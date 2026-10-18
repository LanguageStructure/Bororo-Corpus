#!/usr/bin/env python3
"""Corpus-wide verb paradigm comparison. Read-only; no morpheme boundaries inferred."""
import argparse
import collections
import csv
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", nargs="?", default="CorBo/Corpus_Files/CorBo.conllu")
    ap.add_argument("--out", default="reports/morphology_global")
    ap.add_argument("--min-forms", type=int, default=3)
    args = ap.parse_args()
    source, out = Path(args.source), Path(args.out)
    if not source.is_file():
        ap.error("Missing file: " + str(source))
    out.mkdir(parents=True, exist_ok=True)
    counts = collections.Counter()
    contexts = collections.defaultdict(set)
    sid = ""
    for raw in source.open(encoding="utf-8"):
        line = raw.strip()
        if line.startswith("# sent_id = "):
            sid = line.split("=", 1)[1].strip()
        if not line or line.startswith("#"):
            continue
        c = line.split("\t")
        if len(c) != 10 or not c[0].isdigit() or c[3] != "VERB":
            continue
        form, lemma, feats = c[1], c[2], c[5]
        if lemma == "_" or form == "_":
            continue
        counts[(lemma, form, feats)] += 1
        if sid and len(contexts[(lemma, form, feats)]) < 3:
            contexts[(lemma, form, feats)].add(sid)
    bylemma = collections.defaultdict(list)
    for (lemma, form, feats), n in counts.items():
        bylemma[lemma].append((form, feats, n))
    with (out / "verb_paradigms_review.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(("lemma", "distinct_forms", "lemma_tokens", "form", "feats", "count", "sample_sent_ids", "review_status"))
        for lemma, entries in sorted(bylemma.items(), key=lambda x: (-len({f for f, _, _ in x[1]}), -sum(n for _, _, n in x[1]), x[0])):
            distinct = len({f for f, _, _ in entries})
            if distinct < args.min_forms:
                continue
            total = sum(n for _, _, n in entries)
            for form, feats, n in sorted(entries, key=lambda x: (-x[2], x[0], x[1])):
                w.writerow((lemma, distinct, total, form, feats, n,
                            ";".join(sorted(contexts[(lemma, form, feats)])), "not_morphologically_validated"))
    print("VERB lemmas:", len(bylemma))
    print("VERB lemmas with >= {} forms: {}".format(args.min_forms,
        sum(len({f for f, _, _ in entries}) >= args.min_forms for entries in bylemma.values())))
    print("Report:", out / "verb_paradigms_review.csv")

if __name__ == "__main__":
    main()
