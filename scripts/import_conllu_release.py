#!/usr/bin/env python3
"""Stage a user-supplied CoNLL-U release without modifying existing corpus data.

Usage: python3 scripts/import_conllu_release.py /path/to/latest.conllu
The script checks structural integrity and copies into a versioned corpus path.
It does not overwrite CorBo.conllu, rebuild indexes, or publish the website.
"""
import argparse
import hashlib
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "CorBo/Corpus_Files/CorBo_20261018.conllu"


def inspect(path):
    sentences = 0
    tokens = 0
    malformed = []
    ids = Counter()
    current_id = None
    with path.open(encoding="utf-8-sig") as handle:
        for lineno, raw in enumerate(handle, 1):
            line = raw.rstrip("\r\n")
            if line.startswith("# sent_id ="):
                current_id = line.partition("=")[2].strip()
                ids[current_id] += 1
                sentences += 1
            elif line and not line.startswith("#"):
                cols = line.split("\t")
                if len(cols) != 10:
                    malformed.append(lineno)
                elif cols[0].isdigit():
                    tokens += 1
    return sentences, tokens, malformed, [k for k, n in ids.items() if n > 1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--destination", type=Path, default=DEST)
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    destination = args.destination.expanduser().resolve()
    if not source.is_file():
        parser.error(f"File not found: {source}")
    sentences, tokens, malformed, duplicates = inspect(source)
    print(f"Source: {source}\nSentences with sent_id: {sentences}\nTokens: {tokens}")
    print(f"Malformed token rows: {len(malformed)}; duplicate sent_id: {len(duplicates)}")
    if malformed or duplicates:
        parser.error("Structural issues found; no file copied")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if destination.exists():
        if hashlib.sha256(destination.read_bytes()).hexdigest() == digest:
            print("Identical version already staged:", destination)
            return
        parser.error(f"Destination exists with different contents: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    print(f"Staged: {destination}\nSHA256: {digest}")
    print("Canonical CorBo.conllu and site indexes unchanged; review before activation.")


if __name__ == "__main__":
    main()
