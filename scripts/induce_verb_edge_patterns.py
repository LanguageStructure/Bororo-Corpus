#!/usr/bin/env python3
"""Discover recurring edge differences in attested verbal FEATS contrasts.

Hypotheses are orthographic only, not validated morpheme boundaries.
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

def edge_difference(a, b):
    if a == b:
        return None
    # Require a shared nonempty core and nonempty material on both sides
    # or one zero exponent. Avoid treating unrelated words as alternations.
    for side in ("prefix", "suffix"):
        if side == "prefix":
            common = 0
            while common < min(len(a), len(b)) and a[-1-common] == b[-1-common]:
                common += 1
            if common < 2:
                continue
            x, y = a[:-common], b[:-common]
        else:
            common = 0
            while common < min(len(a), len(b)) and a[common] == b[common]:
                common += 1
            if common < 2:
                continue
            x, y = a[common:], b[common:]
        if x != y and max(len(x), len(y)) <= 8:
            return side, x or "∅", y or "∅", common
    return None

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("contrasts", nargs="?", default="reports/morphology_global/verb_feature_contrasts.csv")
    p.add_argument("--output", default="reports/morphology_global/verb_edge_hypotheses.csv")
    p.add_argument("--min-lemmas", type=int, default=3)
    args = p.parse_args()
    source, output = Path(args.contrasts), Path(args.output)
    if not source.is_file():
        p.error("Missing report: " + str(source))
    groups = defaultdict(list)
    with source.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            a, b = row["example_form_a"], row["example_form_b"]
            if a.casefold() == b.casefold():
                continue
            diff = edge_difference(a.casefold(), b.casefold())
            if not diff:
                continue
            side, left, right, core = diff
            key = (row["feature"], row["value_a"], row["value_b"], side, left, right)
            groups[key].append((row["lemma"], a, b, core, row["count_a"], row["count_b"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    kept = 0
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(("feature", "value_a", "value_b", "edge", "piece_a", "piece_b",
                         "supporting_lemmas", "example_lemmas", "example_forms",
                         "status"))
        for key, examples in sorted(groups.items(), key=lambda kv: (-len(set(x[0] for x in kv[1])), kv[0])):
            lemmas = sorted(set(x[0] for x in examples))
            if len(lemmas) < args.min_lemmas:
                continue
            kept += 1
            writer.writerow((*key, len(lemmas), ";".join(lemmas[:20]),
                             ";".join("{}:{}>{}".format(x[0], x[1], x[2]) for x in examples[:12]),
                             "orthographic_hypothesis_not_validated"))
    print("Edge hypotheses supported by >= {} lemmas: {}".format(args.min_lemmas, kept))
    print("Report:", output)

if __name__ == "__main__":
    main()
