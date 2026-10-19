#!/usr/bin/env python3
"""Audit paradigm forms across CoNLL-U token columns and sentence metadata.

No morphological segmentation is inferred. A metadata hit is textual
attestation, not an individual FORM-token attestation.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "CorBo_vNext/annotations/p012_paradigm_reviewed_20261019.json"
CORPUS = ROOT / "CorBo/Corpus_Files"


def audit(paths, paradigm):
    forms = [item["form"].casefold() for item in paradigm["forms"]]
    counts = {form: {"form_tokens": 0, "text_sentences": 0, "text_examples": [],
                     "split_token_sequences": 0, "split_examples": []} for form in forms}
    for path in paths:
        metadata = {}
        tokens = []
        def flush():
            text = metadata.get("text", "")
            words = [row[1].casefold() for row in tokens]
            for form in forms:
                hit = re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", text.casefold())
                if hit:
                    counts[form]["text_sentences"] += 1
                    if len(counts[form]["text_examples"]) < 3:
                        counts[form]["text_examples"].append({"file": str(path), "sent_id": metadata.get("sent_id"), "text": text})
                # A sequence of multiple annotated tokens can reconstruct the spelling.
                # Require consecutive tokens and exact concatenation.
                for i in range(len(words)):
                    if words[i] == form:
                        continue
                    joined = ""
                    for j in range(i, min(i + 6, len(words))):
                        joined += words[j]
                        if joined == form and j > i:
                            counts[form]["split_token_sequences"] += 1
                            if len(counts[form]["split_examples"]) < 3:
                                counts[form]["split_examples"].append({"file": str(path), "sent_id": metadata.get("sent_id"), "tokens": words[i:j+1]})
                            break
                        if len(joined) >= len(form):
                            break
        with path.open(encoding="utf-8-sig") as stream:
            for line in stream:
                line = line.rstrip("\n")
                if not line:
                    flush()
                    metadata, tokens = {}, []
                elif line.startswith("# "):
                    if " = " in line:
                        k, v = line[2:].split(" = ", 1)
                        metadata[k] = v
                else:
                    cols = line.split("\t")
                    if len(cols) == 10 and cols[0].isdigit():
                        tokens.append(cols)
                        form = cols[1].casefold()
                        if form in counts:
                            counts[form]["form_tokens"] += 1
            if metadata or tokens:
                flush()
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paradigm", type=Path, default=DEFAULT)
    parser.add_argument("--corpus", type=Path, default=CORPUS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paradigm = json.loads(args.paradigm.read_text(encoding="utf-8"))
    paths = sorted(args.corpus.rglob("*.conllu")) if args.corpus.is_dir() else [args.corpus]
    if not paths:
        raise SystemExit("No CoNLL-U files found in " + str(args.corpus))
    result = audit(paths, paradigm)
    for form, row in result.items():
        print(f"{form:12} FORM={row['form_tokens']:5} #text={row['text_sentences']:5} split={row['split_token_sequences']:5}")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"paradigm": paradigm["id"], "files": [str(p) for p in paths],
                                          "results": result}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Report:", args.output)


if __name__ == "__main__":
    main()
