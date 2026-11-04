"""Context-sensitive reviewed morphology for CorBo.

Keep distinct analyses per surface. Reviewed underlying segments may differ
from surface spans; neither is inferred from spelling.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENTRAL = ROOT / "docs/data/morphology-reviewed-20261023.json"
AIMO = ROOT / "CorBo_vNext/annotations/aimo_reviewed_20261018.json"


def load_registry():
    registry = {}
    if CENTRAL.exists():
        entries = json.loads(CENTRAL.read_text(encoding="utf-8"))["entries"]
        for form, item in entries.items():
            if item.get("status") != "confirmed":
                continue
            add(registry, form, {
                "segments": item["segments"],
                "surface_segments": item.get("surface_segments"),
                "lemma": item.get("lemma"),
                "morphophonology": item.get("morphophonology"),
                "source": "morphology-reviewed-20261023",
                "status": "confirmed",
            })
    if AIMO.exists():
        data = json.loads(AIMO.read_text(encoding="utf-8"))
        for paradigm in data.get("paradigms", []):
            for item in paradigm.get("analyses", []):
                add(registry, item["surface"], {
                    "segments": item["segments"],
                    "surface_segments": item["segments"],
                    "lemma": paradigm.get("lexeme"),
                    "person": item.get("person"),
                    "source": "aimo-reviewed-20261018",
                    "status": "confirmed",
                })
    # Explicit contextual confirmation: the atomic ADP and VERB are 3SG,
    # whereas t+o is the reflexive form of nominal lexeme o.
    for upos in ("ADP", "VERB"):
        add(registry, "to", {
            "segments": ["to"], "surface_segments": ["to"],
            "upos": upos, "person": "3SG", "status": "confirmed",
            "source": "linguist-clarification-20261104",
        })
    add(registry, "to", {
        "segments": ["t", "o"], "surface_segments": ["t", "o"],
        "lemma": "o", "person": "3REFL", "status": "confirmed",
        "source": "linguist-clarification-20261104",
    })
    return registry


def add(registry, form, entry):
    form = form.casefold()
    entry = {k: v for k, v in entry.items() if v is not None}
    # Merge exact contextual duplicates, retain conflicting segmentations.
    key = (tuple(entry["segments"]), entry.get("upos"), entry.get("person"), entry.get("lemma"))
    records = registry.setdefault(form, [])
    if not any((tuple(r["segments"]), r.get("upos"), r.get("person"), r.get("lemma")) == key for r in records):
        records.append(entry)


def main():
    registry = load_registry()
    ambiguous = {form: entries for form, entries in registry.items()
                 if len({tuple(e["segments"]) for e in entries}) > 1}
    print(f"{len(registry)} reviewed forms; {len(ambiguous)} forms with alternative segmentations")
    for form in sorted(ambiguous):
        print(form, ":", " / ".join("+".join(e["segments"]) for e in ambiguous[form]))
    assert {"to", "t+o"} == {"+".join(e["segments"]) for e in registry["to"]}


if __name__ == "__main__":
    main()
