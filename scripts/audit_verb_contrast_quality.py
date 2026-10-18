#!/usr/bin/env python3
"""Quality-control contrasts: flag identical forms and weak evidence; no corrections."""
import argparse
import csv
from collections import Counter
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", nargs="?", default="reports/morphology_global/verb_feature_contrasts.csv")
    ap.add_argument("--output", default="reports/morphology_global/verb_contrasts_quality.csv")
    args = ap.parse_args()
    src, dst = Path(args.input), Path(args.output)
    if not src.is_file():
        ap.error("Missing contrast report: " + str(src))
    with src.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or []
    counts = Counter()
    for row in rows:
        a, b = row["example_form_a"], row["example_form_b"]
        na, nb = int(row["count_a"]), int(row["count_b"])
        flags = []
        if a.casefold() == b.casefold():
            flags.append("same_surface_different_feats")
        if min(na, nb) == 1:
            flags.append("singleton_side")
        if not flags:
            flags.append("candidate_for_manual_comparison")
        row["review_flags"] = ";".join(flags)
        for flag in flags:
            counts[flag] += 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns + ["review_flags"])
        writer.writeheader()
        writer.writerows(rows)
    print("Compared rows:", len(rows))
    for flag, count in counts.most_common():
        print("{}: {}".format(flag, count))
    print("Report:", dst)

if __name__ == "__main__":
    main()
