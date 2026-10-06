#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report lexical diversity by CorBo collection using the official corpus tokenization."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNITS = ROOT / "docs" / "data" / "corbo-units.json"
TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?", re.UNICODE)


def normalize_bororo_y(text):
    return str(text or "").replace("Y", "U").replace("y", "u")


def tokens(text):
    return [m.group(0).lower() for m in TOKEN_RE.finditer(normalize_bororo_y(text))]


def summarize(units):
    result = defaultdict(lambda: {"units": 0, "tokens": 0, "types": set()})
    for unit in units:
        collection = unit.get("collection") or "(sem coleção)"
        ts = tokens(unit.get("b", ""))
        row = result[collection]
        row["units"] += 1
        row["tokens"] += len(ts)
        row["types"].update(ts)
    return result


def subset_stats(units):
    ts = []
    for unit in units:
        ts.extend(tokens(unit.get("b", "")))
    types = len(set(ts))
    return len(units), len(ts), types, (100 * types / len(ts) if ts else 0.0)


def main():
    units = json.loads(UNITS.read_text(encoding="utf-8"))
    data = summarize(units)

    print("COLEÇÃO | UNIDADES | TOKENS | TIPOS | TTR")
    print("-" * 76)
    for collection, row in sorted(data.items(), key=lambda item: (-item[1]["tokens"], item[0])):
        ntypes = len(row["types"])
        ttr = 100 * ntypes / row["tokens"] if row["tokens"] else 0.0
        print("{} | {} | {} | {} | {:.2f}%".format(
            collection, row["units"], row["tokens"], ntypes, ttr
        ))

    print()
    print("COMPARAÇÃO PRINCIPAL")
    print("-" * 76)
    comparisons = [
        ("Bakaru Maiwu", [u for u in units if u.get("collection") == "Bakaru Maiwu"]),
        ("Corpus sem Bakaru Maiwu", [u for u in units if u.get("collection") != "Bakaru Maiwu"]),
        ("Corpus total", units),
    ]
    for label, subset in comparisons:
        nunits, ntokens, ntypes, ttr = subset_stats(subset)
        print("{} | unidades={} | tokens={} | tipos={} | TTR={:.2f}%".format(
            label, nunits, ntokens, ntypes, ttr
        ))


if __name__ == "__main__":
    main()
