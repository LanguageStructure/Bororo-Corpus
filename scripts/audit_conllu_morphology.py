#!/usr/bin/env python3
"""Read-only CoNLL-U audit for morphological annotation coverage.

Usage: python3 scripts/audit_conllu_morphology.py [path/to/file.conllu]
Prints aggregate counts only; never modifies source files or publishes examples.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

DEFAULT = Path(__file__).resolve().parents[1] / "CorBo/Corpus_Files/CorBo.conllu"


def main(path: Path) -> None:
    counts = Counter()
    upos = Counter()
    feats_keys = Counter()
    misc_keys = Counter()
    anomalies = Counter()
    seen_ids = set()
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            line = line.rstrip("\n\r")
            if not line:
                continue
            if line.startswith("#"):
                if line.startswith("# sent_id ="):
                    counts["sent_ids"] += 1
                    sent_id = line.partition("=")[2].strip()
                    if sent_id in seen_ids:
                        anomalies["duplicate_sent_ids"] += 1
                    seen_ids.add(sent_id)
                elif line.startswith("# text_por ="):
                    counts["text_por_fields"] += 1
                    if not line.partition("=")[2].strip():
                        counts["empty_text_por"] += 1
                continue
            fields = line.split("\t")
            if len(fields) != 10:
                anomalies["invalid_column_count"] += 1
                continue
            tid, form, lemma, pos, xpos, feats, head, deprel, deps, misc = fields
            if "-" in tid:
                counts["multiword_token_rows"] += 1
                continue
            if "." in tid:
                counts["empty_node_rows"] += 1
                continue
            if not tid.isdigit():
                anomalies["invalid_token_ids"] += 1
                continue
            counts["tokens"] += 1
            upos[pos] += 1
            if lemma != "_":
                counts["with_lemma"] += 1
            if pos != "_":
                counts["with_upos"] += 1
            if feats != "_":
                counts["with_feats"] += 1
                for pair in feats.split("|"):
                    if "=" in pair:
                        feats_keys[pair.split("=", 1)[0]] += 1
                    else:
                        anomalies["malformed_feats_items"] += 1
            if misc != "_":
                counts["with_misc"] += 1
                for pair in misc.split("|"):
                    if "=" in pair:
                        misc_keys[pair.split("=", 1)[0]] += 1
                    else:
                        misc_keys["(flag)"] += 1
            if head != "_" and deprel != "_":
                counts["with_dependency"] += 1
            if lemma != "_" and pos != "_" and feats != "_":
                counts["lemma_upos_feats"] += 1
    print(f"Fonte: {path}")
    for key in ("sent_ids", "tokens", "multiword_token_rows", "empty_node_rows",
                "text_por_fields", "empty_text_por", "with_lemma", "with_upos",
                "with_feats", "with_misc", "with_dependency", "lemma_upos_feats"):
        value = counts[key]
        share = f" ({value / counts['tokens']:.1%} dos tokens)" if key.startswith(("with_", "lemma_upos")) and counts["tokens"] else ""
        print(f"{key}: {value}{share}")
    for title, counter in (("UPOS", upos), ("FEATS keys", feats_keys),
                           ("MISC keys", misc_keys), ("Anomalias", anomalies)):
        print(f"\n{title}:")
        for name, value in counter.most_common(30):
            print(f"  {name}: {value}")
        if not counter:
            print("  nenhuma")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT)
