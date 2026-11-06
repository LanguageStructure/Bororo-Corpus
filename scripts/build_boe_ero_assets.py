#!/usr/bin/env python3
"""Build the Boe Ero public JSON and standalone annotation CoNLL-U.

The canonical source is the parallel TSV.  The CoNLL-U output is deliberately
kept separate from CorBo.conllu: this builder will create it once, verify an
identical generated copy, and refuse to replace a file that may contain manual
annotation.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo_vNext/texts/boe-ero/boe_ero_parallel.tsv"
PUBLIC_JSON = ROOT / "docs/data/boe-ero-units.json"
CONLLU = ROOT / "CorBo_vNext/texts/boe-ero/boe_ero_unannotated.conllu"
REQUIRED_FIELDS = {
    "id",
    "section",
    "title",
    "speaker",
    "translator",
    "source_number",
    "translation_number",
    "source",
    "reviewed",
    "portuguese",
    "editorial_note",
}
ID_RE = re.compile(r"BOR-CORBO-BOE-(\d{2})-(\d{3})\Z")
TOKEN_RE = re.compile(
    r"\.{2,}|[\w\uf000-\uf8ff]+(?:[’'-][\w\uf000-\uf8ff]+)*|[^\w\s]",
    re.UNICODE,
)


def read_rows(path: Path = SOURCE) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = set(reader.fieldnames or ())
        missing = sorted(REQUIRED_FIELDS - fields)
        if missing:
            raise ValueError("Colunas ausentes no TSV Boe Ero: " + ", ".join(missing))
        rows = list(reader)
    validate_rows(rows)
    return rows


def validate_rows(rows: list[dict[str, str]]) -> None:
    ids = [row["id"].strip() for row in rows]
    duplicates = [key for key, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError("IDs Boe Ero duplicados: " + ", ".join(duplicates))
    for row in rows:
        match = ID_RE.fullmatch(row["id"].strip())
        if not match:
            raise ValueError(f"ID Boe Ero inválido: {row['id']!r}")
        if match.group(1) != row["section"].strip().zfill(2):
            raise ValueError(f"Seção e ID divergem em {row['id']}")
        if not row["portuguese"].strip():
            raise ValueError(f"Tradução portuguesa vazia em {row['id']}")


def public_units(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    units = []
    for row in rows:
        reviewed = row["reviewed"].strip()
        source = row["source"].strip()
        units.append(
            {
                "id": row["id"].strip(),
                "b": reviewed or source,
                "source": source,
                "p": row["portuguese"].strip(),
                "collection": "Boe Ero",
                "group": "Documentary texts",
                "allow_empty_b": not bool(source),
                "section": row["section"].strip(),
                "title": row["title"].strip(),
                "speaker": row["speaker"].strip(),
                "translator": row["translator"].strip(),
                "source_number": row["source_number"].strip(),
                "translation_number": row["translation_number"].strip(),
                "editorial_note": row["editorial_note"].strip(),
                "reviewed": bool(reviewed),
                "status": "reviewed" if reviewed else "provisional",
            }
        )
    return units


def conllu_tokens(text: str) -> list[tuple[str, str]]:
    matches = list(TOKEN_RE.finditer(text))
    tokens = []
    for index, match in enumerate(matches):
        has_next = index + 1 < len(matches)
        next_start = matches[index + 1].start() if has_next else len(text)
        misc = "SpaceAfter=No" if has_next and match.end() == next_start else "_"
        tokens.append((match.group(0), misc))
    return tokens


def clean_comment(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def render_conllu(rows: list[dict[str, str]]) -> tuple[str, int, int, list[str]]:
    blocks = []
    token_count = 0
    skipped = []
    for row in rows:
        source = row["source"].strip()
        reviewed = row["reviewed"].strip()
        if not source:
            skipped.append(row["id"].strip())
            continue
        text = reviewed or source
        tokens = conllu_tokens(text)
        if not tokens:
            raise ValueError(f"Unidade sem tokens: {row['id']}")
        comments = [
            f"# sent_id = {row['id'].strip()}",
            f"# text = {clean_comment(text)}",
            f"# text_por = {clean_comment(row['portuguese'])}",
            "# collection = Boe Ero",
            f"# section = {row['section'].strip()}",
            f"# title = {clean_comment(row['title'])}",
            f"# speaker = {clean_comment(row['speaker'])}",
            f"# translator = {clean_comment(row['translator'])}",
            f"# source_number = {row['source_number'].strip()}",
            f"# translation_number = {row['translation_number'].strip()}",
            f"# editorial_status = {'reviewed' if reviewed else 'provisional'}",
        ]
        if reviewed and reviewed != source:
            comments.append(f"# text_source = {clean_comment(source)}")
        if row["editorial_note"].strip():
            comments.append(f"# editorial_note = {clean_comment(row['editorial_note'])}")
        token_lines = []
        for token_id, (form, misc) in enumerate(tokens, 1):
            token_lines.append(
                "\t".join((str(token_id), form, "_", "_", "_", "_", "_", "_", "_", misc))
            )
        blocks.append("\n".join(comments + token_lines))
        token_count += len(tokens)
    return "\n\n".join(blocks) + "\n", len(blocks), token_count, skipped


def write_or_check(path: Path, content: str, *, check: bool, protect: bool = False) -> str:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return "ok"
    if check:
        raise ValueError(f"Artefato desatualizado ou ausente: {path.relative_to(ROOT)}")
    if protect and current is not None:
        raise ValueError(
            f"Recusado sobrescrever {path.relative_to(ROOT)}: o arquivo pode conter anotação manual. "
            "Use outro --conllu-output para gerar uma cópia nova."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "written"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--public-json", type=Path, default=PUBLIC_JSON)
    parser.add_argument("--conllu-output", type=Path, default=CONLLU)
    parser.add_argument("--check", action="store_true", help="Validate without writing files.")
    args = parser.parse_args()

    rows = read_rows(args.source)
    public = json.dumps(public_units(rows), ensure_ascii=False, separators=(",", ":"))
    conllu, blocks, tokens, skipped = render_conllu(rows)
    json_result = write_or_check(args.public_json, public, check=args.check)
    conllu_result = write_or_check(
        args.conllu_output, conllu, check=args.check, protect=True
    )
    print(
        f"Boe Ero: {len(rows)} unidades paralelas; {blocks} blocos CoNLL-U; "
        f"{tokens} tokens; lacunas sem Bororo: {', '.join(skipped) or 'nenhuma'}. "
        f"JSON={json_result}; CoNLL-U={conllu_result}."
    )


if __name__ == "__main__":
    main()
