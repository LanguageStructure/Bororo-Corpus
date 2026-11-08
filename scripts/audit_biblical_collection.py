#!/usr/bin/env python3
"""Audit the documentary biblical collection without modifying source material.

Usage: python3 scripts/audit_biblical_collection.py
The documentary paragraphs are NOT CoNLL-U annotated sentences.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BOOKS = ROOT / "CorBo_vNext" / "texts" / "biblicos"
SOURCES = ROOT / "CorBo" / "Scripture_Sources"


def paragraphs(text):
    return [p.strip() for p in re.split(r"\r?\n\s*\r?\n", text) if p.strip()]


def main():
    problems = []
    rows = []
    catalog = (DOCS / "catalogo.html").read_text(encoding="utf-8")
    editor = (ROOT / "scripts" / "corbo_editor.py").read_text(encoding="utf-8")
    home = (DOCS / "index.html").read_text(encoding="utf-8")
    stats = (DOCS / "statistics.html").read_text(encoding="utf-8")
    for path in sorted(BOOKS.glob("*/*_unidades_documentais.json")):
        slug = path.parent.name
        data = json.loads(path.read_text(encoding="utf-8"))
        public = DOCS / "data" / f"{slug}.json"
        reader = DOCS / f"{slug}.html"
        if not public.is_file() or not reader.is_file():
            problems.append(f"{slug}: missing public JSON or reader")
            continue
        if json.loads(public.read_text(encoding="utf-8")) != data:
            problems.append(f"{slug}: public JSON differs from canonical JSON")
        if f'{slug}.html' not in catalog:
            problems.append(f"{slug}: missing catalog link")
        if f"'{slug}':" not in editor:
            problems.append(f"{slug}: missing editor mapping")
        if slug not in home or slug not in stats:
            problems.append(f"{slug}: missing dynamic statistics inclusion")
        units = data.get("units", [])
        ids = [u.get("id") for u in units]
        if len(ids) != len(set(ids)):
            problems.append(f"{slug}: duplicate unit IDs")
        source = ROOT / data.get("source", "")
        if not source.is_file():
            problems.append(f"{slug}: missing source file {source}")
        else:
            original = paragraphs(source.read_text(encoding="utf-8"))
            if len(original) != len(units):
                problems.append(f"{slug}: {len(original)} source paragraphs != {len(units)} units")
            if [u.get("source_text_original") for u in units] != original:
                problems.append(f"{slug}: source paragraphs changed or reordered")
            counts = Counter(original)
            if any(u.get("duplicate_text_count") != counts[u.get("source_text_original")] for u in units):
                problems.append(f"{slug}: duplicate-text counts inconsistent")
        rows.append({"book": data.get("book", slug), "slug": slug, "units": len(units)})
    report = {"books": len(rows), "documentary_units": sum(r["units"] for r in rows),
              "books_detail": rows, "problems": problems,
              "note": "Documentary units are original paragraphs, not UD-annotated sentences."}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
