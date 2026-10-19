#!/usr/bin/env python3
"""Lookup reviewed lexical paradigms separately from tokenizer segmentation.

Paradigm membership does not license morpheme boundaries.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "CorBo_vNext/annotations/ogwa_paradigm_reviewed_20261019.json"


def load_paradigm(path=REVIEWED):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("review", {}).get("status") != "linguist_confirmed_paradigm_membership":
        raise ValueError("Paradigm membership is not confirmed")
    for entry in data["forms"]:
        if entry.get("segmentation") is not None:
            raise ValueError("This loader handles unsegmented paradigm membership only")
    return data


def lookup(form, paradigm=None):
    paradigm = paradigm if paradigm is not None else load_paradigm()
    key = form.casefold()
    return [{
        "form": item["form"],
        "lemma": paradigm["lemma"],
        "person": item["person"],
        "gloss_pt": item["gloss_pt"],
        "paradigm_id": paradigm["id"],
        "recognition_status": paradigm["review"]["status"],
        "segmentation": None,
        "segmentation_status": "not_reviewed",
        "source": paradigm["source"],
    } for item in paradigm["forms"] if item["form"].casefold() == key]


if __name__ == "__main__":
    import sys
    for word in sys.argv[1:] or ["ioga", "pao", "ao"]:
        print(json.dumps({"query": word, "analyses": lookup(word)}, ensure_ascii=False))
