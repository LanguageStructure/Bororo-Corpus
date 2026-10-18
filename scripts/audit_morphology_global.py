#!/usr/bin/env python3
"""Read-only global inventory of CoNLL-U paradigms; no inferred segmentation is validated."""
import argparse
import collections
import csv
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("conllu", nargs="?", default="CorBo/Corpus_Files/CorBo.conllu")
    p.add_argument("--out", default="reports/morphology_global")
    args = p.parse_args()
    src, out = Path(args.conllu), Path(args.out)
    if not src.is_file():
        p.error("CoNLL-U not found: " + str(src))
    out.mkdir(parents=True, exist_ok=True)
    forms = collections.Counter()
    paradigms = collections.defaultdict(lambda: collections.Counter())
    feats_bad = collections.Counter()
    stats = collections.Counter()
    with src.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n\r")
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) != 10:
                stats["invalid_lines"] += 1
                continue
            tid, form, lemma, upos, xpos, feats = cols[:6]
            if not tid.isdigit():
                continue  # MWT and empty nodes are not ordinary word tokens
            stats["tokens"] += 1
            if upos == "PUNCT":
                continue
            stats["lexical_tokens"] += 1
            key = (lemma, upos)
            paradigms[key][(form, feats)] += 1
            forms[(form, lemma, upos, feats)] += 1
            if feats != "_":
                pieces = feats.split("|")
                if any(not x or "=" not in x or not x.split("=", 1)[0] or not x.split("=", 1)[1] for x in pieces):
                    feats_bad[(lemma, form, feats)] += 1
                    stats["malformed_feats_tokens"] += 1
    with (out / "form_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(("form", "lemma", "upos", "feats", "count"))
        for (form, lemma, upos, feats), n in sorted(forms.items(), key=lambda x: (-x[1], x[0])):
            w.writerow((form, lemma, upos, feats, n))
    with (out / "lemma_paradigms.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(("lemma", "upos", "tokens", "distinct_forms", "distinct_form_feats", "forms_with_counts"))
        for (lemma, upos), items in sorted(paradigms.items(), key=lambda x: (-sum(x[1].values()), x[0])):
            surface = collections.Counter()
            for (form, feats), n in items.items(): surface[form] += n
            w.writerow((lemma, upos, sum(items.values()), len(surface), len(items),
                        "; ".join("{}:{}".format(k, v) for k, v in surface.most_common())))
    with (out / "feats_review.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(("lemma", "form", "feats", "count"))
        for key, n in sorted(feats_bad.items(), key=lambda x: (-x[1], x[0])):
            w.writerow((*key, n))
    stats["lemma_upos_pairs"] = len(paradigms)
    stats["distinct_form_analyses"] = len(forms)
    for k, v in sorted(stats.items()): print("{}: {}".format(k, v))
    print("Reports:", out)

if __name__ == "__main__":
    main()
