#!/usr/bin/env python3
"""Compare attested verb forms across FEATS bundles and lemmas; read-only.

The report is evidence for review, not an automatic morphological analysis.
"""
import argparse
from collections import Counter, defaultdict
import csv
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("conllu", nargs="?", default="CorBo/Corpus_Files/CorBo.conllu")
    ap.add_argument("--out", default="reports/morphology_global")
    ap.add_argument("--min-lemmas", type=int, default=3)
    args = ap.parse_args()
    src, out = Path(args.conllu), Path(args.out)
    if not src.is_file():
        ap.error("File not found: " + str(src))
    out.mkdir(parents=True, exist_ok=True)
    forms = defaultdict(Counter)
    for line in src.open(encoding="utf-8"):
        cols = line.rstrip("\r\n").split("\t")
        if len(cols) != 10 or not cols[0].isdigit() or cols[3] != "VERB":
            continue
        form, lemma, feats = cols[1], cols[2], cols[5]
        if "_" in (form, lemma, feats):
            continue
        parts = feats.split("|")
        if any("=" not in part or not all(part.split("=", 1)) for part in parts):
            continue
        normalized = "|".join(sorted(parts))
        forms[(lemma, normalized)][form] += 1
    # A pair of FEATS bundles must be attested for the same lemma.
    by_lemma = defaultdict(dict)
    for (lemma, feats), counts in forms.items():
        by_lemma[lemma][feats] = counts
    contrasts = defaultdict(list)
    for lemma, bundles in by_lemma.items():
        keys = sorted(bundles)
        for i, left in enumerate(keys):
            for right in keys[i + 1:]:
                # Compare only bundles differing in exactly one feature key/value.
                a = dict(p.split("=", 1) for p in left.split("|"))
                b = dict(p.split("=", 1) for p in right.split("|"))
                changed = [k for k in a.keys() | b.keys() if a.get(k) != b.get(k)]
                if len(changed) != 1:
                    continue
                k = changed[0]
                contrasts[(k, a.get(k, "∅"), b.get(k, "∅"))].append(
                    (lemma, left, right, bundles[left].most_common(1)[0],
                     bundles[right].most_common(1)[0]))
    report = out / "verb_feature_contrasts.csv"
    with report.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(("feature", "value_a", "value_b", "supporting_lemmas",
                    "lemma", "feats_a", "feats_b", "example_form_a",
                    "count_a", "example_form_b", "count_b", "status"))
        for (feature, va, vb), examples in sorted(
            contrasts.items(), key=lambda item: (-len(item[1]), item[0])):
            if len(examples) < args.min_lemmas:
                continue
            for lemma, fa, fb, (forma, na), (formb, nb) in sorted(examples):
                w.writerow((feature, va, vb, len(examples), lemma, fa, fb,
                            forma, na, formb, nb, "comparison_only_not_segmentation"))
    print("Verb lemmas with valid FEATS:", len(by_lemma))
    print("One-feature contrasts:", len(contrasts))
    print("Contrasts supported by >= {} lemmas: {}".format(
        args.min_lemmas, sum(len(v) >= args.min_lemmas for v in contrasts.values())))
    print("Report:", report)

if __name__ == "__main__":
    main()
