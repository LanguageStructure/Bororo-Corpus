#!/usr/bin/env python3
"""Build an attested FORM → (LEMMA, UPOS, FEATS) index from CoNLL-U.

Usage: python3 scripts/build_grammatical_index.py [input.conllu] [output.json]
The output contains observations, not validated morpheme boundaries.
No input is modified. Empty/invalid FEATS are retained as raw evidence,
not silently normalized into grammatical claims.
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUTPUT = ROOT / "docs/data/grammatical-index.json"


def build(path: Path):
    observations = defaultdict(Counter)
    examples = defaultdict(list)
    sentences = 0
    tokens = 0
    malformed = 0
    sent_id = ""
    for line in path.open(encoding="utf-8-sig"):
        line = line.rstrip("\r\n")
        if line.startswith("# sent_id = "):
            sent_id = line.partition("=")[2].strip()
            sentences += 1
            continue
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 10 or not cols[0].isdigit():
            continue
        form, lemma, upos, feats = cols[1], cols[2], cols[3], cols[5]
        if form == "_" or not form:
            continue
        tokens += 1
        # Reject malformed FEATS as structured categories; preserve the raw
        # string and explicitly flag it for editorial review.
        valid = feats == "_" or all(
            "=" in item and item.split("=", 1)[0] and item.split("=", 1)[1]
            for item in feats.split("|")
        )
        if not valid:
            malformed += 1
        key = (lemma if lemma != "_" else "", upos if upos != "_" else "",
               feats if feats != "_" else "", valid)
        normalized = form.casefold()
        observations[normalized][key] += 1
        if len(examples[(normalized, key)]) < 3 and sent_id:
            examples[(normalized, key)].append(sent_id)
    lexicon = {}
    for form, variants in sorted(observations.items()):
        analyses = []
        for (lemma, upos, feats, valid), freq in variants.most_common():
            analyses.append({
                "lemma": lemma, "upos": upos, "feats": feats,
                "feats_well_formed": valid, "frequency": freq,
                "sent_ids": examples[(form, (lemma, upos, feats, valid))]
            })
        lexicon[form] = {"frequency": sum(variants.values()), "analyses": analyses}
    return {
        "schema": "corbo-grammatical-index/v1",
        "source": "CorBo/Corpus_Files/CorBo.conllu" if path.resolve() == SOURCE.resolve() else path.name,
        "tokens": tokens, "sentences_with_id": sentences,
        "forms": len(lexicon), "malformed_feats_tokens": malformed,
        "status": "corpus_attested_not_morphologically_segmented",
        "lexicon": lexicon
    }


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    if not source.is_file():
        raise SystemExit(f"Arquivo inexistente: {source}")
    result = build(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{result['tokens']} tokens; {result['forms']} formas; "
          f"{result['malformed_feats_tokens']} FEATS malformados -> {output}")


if __name__ == "__main__":
    main()
