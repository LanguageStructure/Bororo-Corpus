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
INPUTS = [ROOT / "CorBo_vNext" / "texts" / "coqueiro" / "coqueiro_parallel.tsv"]
OUT = ROOT / "docs" / "data"
TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?", re.UNICODE)
CANONICAL_HEADER = ["id", "bororo", "portuguese"]


def tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text or "")]


def read_units() -> list[dict[str, str]]:
    units: list[dict[str, str]] = []
    for path in INPUTS:
        if not path.exists():
            raise SystemExit(f"Canonical TSV not found: {path}")
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            if reader.fieldnames != CANONICAL_HEADER:
                raise SystemExit(
                    f"Canonical TSV {path} must have exactly this header: "
                    + "\t".join(CANONICAL_HEADER)
                )
            for line_no, row in enumerate(reader, start=2):
                if None in row:
                    raise SystemExit(f"Malformed TSV row at {path}:{line_no}")
                uid = (row["id"] or "").strip()
                bor = (row["bororo"] or "").strip()
                por = (row["portuguese"] or "").strip()
                if not uid:
                    raise SystemExit(f"Blank corpus ID at {path}:{line_no}")
                if not bor:
                    raise SystemExit(f"Blank Bororo text at {path}:{line_no} ({uid})")
                units.append({"id": uid, "b": bor, "p": por})
    ids = [u["id"] for u in units]
    if len(ids) != len(set(ids)):
        duplicates = sorted({x for x in ids if ids.count(x) > 1})
        raise SystemExit("Duplicate corpus IDs detected: " + ", ".join(duplicates[:20]))
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
