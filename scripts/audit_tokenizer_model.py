#!/usr/bin/env python3
"""Non-destructive quality audit for a CorBo tokenizer model.

Usage:
  python3 scripts/audit_tokenizer_model.py --model docs/data/tokenizer-model.json
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def audit(model):
    lexicon = model.get("lexicon", {})
    candidates = model.get("candidates", {})
    reviewed = model.get("reviewed_analyses", {})
    issues = []
    counts = Counter()
    underlying_nonconcatenative = []

    for form, candidate in sorted(candidates.items()):
        counts["candidates"] += 1
        segments = candidate.get("segments", [])
        status = candidate.get("status", "")
        if form not in lexicon:
            issues.append((form, "unattested_candidate", status, "+".join(segments)))
        if not segments or not all(isinstance(x, str) and x for x in segments):
            issues.append((form, "invalid_segments", status, repr(segments)))
            continue
        surface = candidate.get("surface_segments")
        if surface is not None:
            if not isinstance(surface, list) or not surface or not all(isinstance(x, str) and x for x in surface):
                issues.append((form, "invalid_surface_segments", status, repr(surface)))
            elif "".join(surface) != form:
                issues.append((form, "surface_mismatch", status, "+".join(surface)))
        elif "".join(segments) != form:
            # The model's segments may be underlying morphemes. Without
            # surface_segments, do not classify morphophonology as an error.
            counts["underlying_nonconcatenative"] += 1
            underlying_nonconcatenative.append((form, status, "+".join(segments)))
        if status == "linguistically_confirmed":
            counts["confirmed_candidates"] += 1
        else:
            counts["proposed_candidates"] += 1
        if candidate.get("evidence_grade") == "unrated":
            counts["unrated_candidates"] += 1

    for form, analyses in sorted(reviewed.items()):
        if form not in lexicon:
            issues.append((form, "reviewed_unattested", "", ""))
        alternatives = {tuple(x.get("segments", [])) for x in analyses}
        if len(alternatives) > 1:
            counts["ambiguous_reviewed_forms"] += 1
        for record in analyses:
            surface = record.get("surface_segments")
            if surface is not None and "".join(surface) != form:
                issues.append((form, "reviewed_surface_mismatch", record.get("status", ""), "+".join(surface)))
    if "to" in reviewed:
        analyses = {tuple(x.get("segments", [])) for x in reviewed["to"]}
        if not {("to",), ("t", "o")}.issubset(analyses):
            issues.append(("to", "missing_contextual_alternative", "", repr(sorted(analyses))))
    return counts, issues, underlying_nonconcatenative


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path("docs/data/tokenizer-model.json"))
    parser.add_argument("--report", type=Path, default=Path("tokenizer_model_audit.json"))
    parser.add_argument("--issues", type=Path, default=Path("tokenizer_model_issues.csv"))
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    counts, issues, underlying_nonconcatenative = audit(model)
    report = {
        "model": str(args.model),
        "source": model.get("source"),
        "source_sha256": model.get("source_sha256"),
        "types": model.get("types"),
        "tokens": model.get("tokens"),
        "counts": dict(counts),
        "issue_count": len(issues),
        "underlying_nonconcatenative_examples": [
            {"form": form, "status": status, "underlying_segments": segments}
            for form, status, segments in underlying_nonconcatenative
        ],
        "notes": [
            "This is a structural audit, not an accuracy or precision estimate.",
            "Underlying morphemes may differ from surface spans; this is reported separately, not counted as an error.",
            "Only explicit surface_segments are required to concatenate to the surface form.",
            "No candidate or corpus data are modified.",
        ],
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with args.issues.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["form", "issue", "status", "detail"])
        writer.writerows(issues)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
