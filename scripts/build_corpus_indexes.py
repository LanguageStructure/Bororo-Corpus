#!/usr/bin/env python3
"""Build derived CorBo web indexes from canonical TSV data.

Canonical corpus data remain TSV. JSON files under docs/data are generated
artifacts for the static explorer and should not be edited by hand.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = [
    ROOT / "CorBo_vNext" / "texts" / "coqueiro" / "coqueiro_parallel.tsv",
]
OUT = ROOT / "docs" / "data"
TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?", re.UNICODE)


def tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text or "")]


def read_units() -> list[dict[str, str]]:
    units: list[dict[str, str]] = []
    for path in INPUTS:
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                uid = (row.get("id") or "").strip()
                bor = (row.get("bororo") or row.get("reviewed_bororo") or "").strip()
                por = (row.get("portuguese") or row.get("portugues") or "").strip()
                if uid and bor:
                    units.append({"id": uid, "b": bor, "p": por})
    ids = [u["id"] for u in units]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate corpus IDs detected; indexes not written.")
    return units


def main() -> None:
    units = read_units()
    if not units:
        raise SystemExit("No canonical corpus units found; indexes not written.")

    counts: Counter[str] = Counter()
    unit_counts: Counter[str] = Counter()
    for unit in units:
        ts = tokens(unit["b"])
        counts.update(ts)
        unit_counts.update(set(ts))

    forms = [
        {"form": form, "frequency": freq, "units": unit_counts[form]}
        for form, freq in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    ]
    stats = {
        "units": len(units),
        "tokens": sum(counts.values()),
        "types": len(counts),
        "collections": ["Coqueiro"],
        "top_forms": forms,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "coqueiro-units.json").write_text(
        json.dumps(units, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (OUT / "coqueiro-stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    print(f"Built {len(units)} units, {stats['tokens']} tokens, {stats['types']} forms")


if __name__ == "__main__":
    main()
