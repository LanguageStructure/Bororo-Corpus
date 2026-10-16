#!/usr/bin/env python3
"""Sentence-held-out lexical baseline; NOT morpheme segmentation accuracy."""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import hashlib, json, argparse

def sentences(path):
    rows, sid = [], None
    for line in path.open(encoding="utf-8-sig"):
        line = line.rstrip("\n")
        if not line:
            if rows: yield sid, rows
            rows, sid = [], None
        elif line.startswith("# sent_id ="):
            sid = line.partition("=")[2].strip()
        elif not line.startswith("#"):
            cols = line.split("\t")
            if len(cols) == 10 and cols[0].isdigit() and cols[1] != "_":
                rows.append((cols[1].casefold(), cols[2].casefold(), cols[3]))
    if rows: yield sid, rows

def evaluate(path):
    train, test = defaultdict(Counter), []
    ntrain = ntest = 0
    for index, (sid, rows) in enumerate(sentences(path)):
        key = sid or f"no-id:{index}"
        heldout = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % 5 == 0
        if heldout:
            test.extend(rows); ntest += 1
        else:
            ntrain += 1
            for form, lemma, upos in rows:
                if lemma != "_" and upos != "_": train[form][(lemma, upos)] += 1
    eligible = covered = correct = 0
    unseen = Counter()
    for form, lemma, upos in test:
        if lemma == "_" or upos == "_": continue
        eligible += 1
        if form in train:
            covered += 1
            correct += train[form].most_common(1)[0][0] == (lemma, upos)
        else: unseen[form] += 1
    ambiguous = sorted(
        ({"form": f, "analyses": len(c), "tokens": sum(c.values())}
         for f,c in train.items() if len(c)>1),
        key=lambda x:(-x["tokens"],x["form"]))
    return {
        "evaluation": "held-out lexical FORM -> (LEMMA,UPOS); NOT morpheme boundaries",
        "train_sentences": ntrain, "test_sentences": ntest,
        "test_tokens_with_gold_lemma_upos": eligible,
        "known_form_test_tokens": covered,
        "known_form_coverage": covered/eligible if eligible else None,
        "exact_lemma_upos_correct": correct,
        "accuracy_on_known_forms": correct/covered if covered else None,
        "accuracy_on_all_eligible_test_tokens": correct/eligible if eligible else None,
        "unseen_form_types": len(unseen), "top_unseen_forms": unseen.most_common(40),
        "ambiguous_form_types_in_training": len(ambiguous),
        "top_ambiguous_forms": ambiguous[:40],
        "morpheme_boundary_accuracy": None,
        "note": "Morpheme boundary accuracy requires manually segmented gold examples."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("conllu", nargs="?", default="CorBo/Corpus_Files/CorBo.conllu")
    ap.add_argument("--output", default="docs/data/tokenizer-evaluation.json")
    args=ap.parse_args()
    result=evaluate(Path(args.conllu))
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list)},indent=2))

if __name__=="__main__": main()
