#!/usr/bin/env python3
"""Stage an annotated CorBo CoNLL-U and rebuild dependent public assets.

Usage: python3 scripts/stage_conllu_release.py /path/to/latest.conllu
Does not commit, push, tag, publish a release, or change the source file.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
REPORT = ROOT / "CorBo_vNext/annotations/latest_conllu_import_report.json"
BUILDERS = [
    ["scripts/build_corpus_indexes.py"],
    ["scripts/train_tokenizer.py"],
    ["scripts/build_grammatical_index.py"],
]

def audit(path):
    tokens = 0
    bad = []
    ids = Counter()
    with path.open(encoding="utf-8-sig") as stream:
        for number, line in enumerate(stream, 1):
            if line.startswith("# sent_id ="):
                ids[line.split("=", 1)[1].strip()] += 1
            elif line.strip() and not line.startswith("#"):
                cols = line.rstrip("\r\n").split("\t")
                if len(cols) != 10:
                    bad.append(number)
                else:
                    tokens += 1
    return {
        "tokens": tokens,
        "sent_id_occurrences": sum(ids.values()),
        "duplicate_sent_ids": [key for key, count in ids.items() if count > 1],
        "invalid_token_lines": bad,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--allow-duplicate-ids", action="store_true",
                        help="Only if deliberately accepted after inspection.")
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    if not source.is_file():
        parser.error("Arquivo CoNLL-U não encontrado")
    result = audit(source)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["invalid_token_lines"]:
        raise SystemExit("Abortado: linhas de tokens sem 10 colunas")
    if result["duplicate_sent_ids"] and not args.allow_duplicate_ids:
        raise SystemExit("Abortado: sent_id duplicados; não modificar o corpus canônico")
    if not result["tokens"]:
        raise SystemExit("Abortado: arquivo sem tokens")
    CANONICAL.parent.mkdir(parents=True, exist_ok=True)
    if CANONICAL.exists():
        backup = CANONICAL.with_suffix(".conllu.pre_update_backup")
        shutil.copy2(CANONICAL, backup)
        print("Backup local:", backup)
    shutil.copy2(source, CANONICAL)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "source_filename": source.name,
        "imported_at_utc": datetime.now(timezone.utc).isoformat(),
        **result,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cmd in BUILDERS:
        print("Executando:", *cmd, flush=True)
        subprocess.run([sys.executable, *cmd], cwd=ROOT, check=True)
    print("Atualização local concluída. Confira git diff e os resultados antes de commit/tag/release.")

if __name__ == "__main__":
    main()
