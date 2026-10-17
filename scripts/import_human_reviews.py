#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import browser review interchange into a versionable, explicitly unverified manifest.

No CoNLL-U token rows are modified. Imported 'revisado' is never treated as
authenticated verification; a human must confirm it separately.
"""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
DEFAULT_MANIFEST = ROOT / "CorBo_vNext/annotations/human_review_imports.tsv"
FIELDS = ["sent_id", "imported_status", "note", "imported_at", "source_file", "verification_status"]


def read_ids(path):
    ids, duplicate = set(), set()
    for line in path.open(encoding="utf-8-sig"):
        if line.startswith("# sent_id ="):
            sid = line.split("=", 1)[1].strip()
            if sid in ids:
                duplicate.add(sid)
            ids.add(sid)
    return ids, duplicate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON exported by the public coverage dashboard")
    parser.add_argument("--conllu", type=Path, default=DEFAULT_CONLLU)
    parser.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--apply", action="store_true", help="Write versionable TSV (default: dry run)")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Arquivo JSON não encontrado: {args.input}. Exporte-o em docs/coverage.html → Revisão humana → Exportar registro JSON. Se ainda não há revisões, não é necessário importar.")
    if not args.conllu.is_file():
        parser.error(f"Arquivo CoNLL-U não encontrado: {args.conllu}. Informe o caminho correto com --conllu.")
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeError) as exc:
        parser.error(f"JSON inválido: {exc}")
    if data.get("format") != "corbo-human-review-v1" or not isinstance(data.get("reviews"), dict):
        parser.error("Unsupported review interchange format")
    ids, duplicates = read_ids(args.conllu)
    now = datetime.now(timezone.utc).isoformat()
    accepted, rejected = [], []
    for sid, record in data["reviews"].items():
        if not isinstance(record, dict) or sid not in ids or sid in duplicates or record.get("status") not in ("revisado", "pendente"):
            rejected.append(sid)
            continue
        accepted.append({
            "sent_id": sid,
            "imported_status": record["status"],
            "note": str(record.get("note") or "")[:2000],
            "imported_at": now,
            "source_file": args.input.name,
            "verification_status": "unverified",
        })
    print(f"Accepted: {len(accepted)}; rejected: {len(rejected)}; duplicate CoNLL-U IDs: {len(duplicates)}")
    if rejected:
        print("Rejected IDs:", ", ".join(rejected[:30]))
    if not accepted:
        print("Nenhuma revisão válida a importar; nenhum arquivo será alterado.")
        return
    if not args.apply:
        print("DRY RUN: use --apply to write the TSV.")
        return
    existing = {}
    if args.output.exists():
        with args.output.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                existing[row["sent_id"]] = row
    for row in accepted:
        existing[row["sent_id"]] = row
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(existing[sid] for sid in sorted(existing))
    print("Saved unverified imports:", args.output)


if __name__ == "__main__":
    main()
