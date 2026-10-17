#!/usr/bin/env python3
"""Read-only concordance for Bororo person proclitics and onset alternations.

Usage: python3 scripts/audit_proclitic_paradigms.py [input.conllu] [output.csv]
The output is evidence for manual review, not a morphological analyzer.
No CoNLL-U data or tokenizer model is modified.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUTPUT = ROOT / "reports/proclitic_paradigms.csv"
# Surface cues are intentionally broad; every hit requires linguistic review.
CUES = ("ce", "pa", "ta", "etu", "tu", "i", "a", "u", "e")
REVIEWED = {
    "itonaregedu": "it+onarege+du",
    "iorudukare": "i+jorudu+ka+re",
    "iorudumodukare": "i+jorudu+modu+ka+re",
    "nure": "nu+re",
}
EXCLUDED = {"iakore", "eakore", "tabiapagado", "ibiapagare"}


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    if not source.is_file():
        raise SystemExit(f"Arquivo não encontrado: {source}")
    rows = []
    sid, text = "", ""
    with source.open(encoding="utf-8-sig") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.rstrip("\r\n")
            if not line:
                sid, text = "", ""
                continue
            if line.startswith("# sent_id ="):
                sid = line.partition("=")[2].strip()
                continue
            if line.startswith("# text ="):
                text = line.partition("=")[2].strip()
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) != 10 or not cols[0].isdigit():
                continue
            form = cols[1].casefold()
            if form in EXCLUDED:
                cue, status = "excluded", "unexpected_attestation_review"
            elif form in REVIEWED:
                cue, status = "reviewed", "explicit_confirmed_analysis"
            else:
                cue = next((p for p in CUES if form.startswith(p) and len(form) > len(p) + 2), "")
                if not cue:
                    continue
                status = "surface_candidate_not_validated"
            rows.append({
                "line": line_number, "sent_id": sid, "token_id": cols[0],
                "form": cols[1], "lemma": cols[2], "upos": cols[3],
                "feats": cols[5], "cue": cue, "status": status,
                "confirmed_segmentation": REVIEWED.get(form, ""),
                "text": text,
            })
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "line", "sent_id", "token_id", "form", "lemma", "upos",
            "feats", "cue", "status", "confirmed_segmentation", "text",
        ])
        writer.writeheader()
        writer.writerows(rows)
    # A second, much smaller review queue requires an independently attested
    # lemma and at least two distinct forms in its annotated family.
    # These are still candidates, not validated morphological boundaries.
    lemma_forms = {}
    for row in rows:
        lemma = row["lemma"].casefold()
        if lemma and lemma != "_":
            lemma_forms.setdefault(lemma, set()).add(row["form"].casefold())
    selected = []
    for row in rows:
        lemma = row["lemma"].casefold()
        form = row["form"].casefold()
        if row["status"] == "explicit_confirmed_analysis":
            selected.append(row)
        elif (row["status"] == "surface_candidate_not_validated"
              and lemma not in ("", "_") and lemma != form
              and len(lemma_forms.get(lemma, ())) >= 2
              and form.startswith(row["cue"])
              and len(form) > len(row["cue"]) + 2):
            selected.append(row)
    shortlist = output.with_name(output.stem + "_lemma_shortlist.csv")
    with shortlist.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "line", "sent_id", "token_id", "form", "lemma", "upos",
            "feats", "cue", "status", "confirmed_segmentation", "text",
        ])
        writer.writeheader()
        writer.writerows(selected)
    # Group the shortlist by lemma and cue for an actionable paradigm overview.
    grouped = {}
    for row in selected:
        key = (row["lemma"].casefold(), row["cue"], row["upos"])
        entry = grouped.setdefault(key, {"tokens": 0, "forms": set(), "sent_ids": set()})
        entry["tokens"] += 1
        entry["forms"].add(row["form"].casefold())
        if row["sent_id"]:
            entry["sent_ids"].add(row["sent_id"])
    summary = output.with_name(output.stem + "_paradigm_summary.csv")
    with summary.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["lemma", "cue", "upos", "tokens", "distinct_forms", "forms", "example_sent_ids"])
        for (lemma, cue, upos), entry in sorted(grouped.items(),
                key=lambda pair: (-len(pair[1]["forms"]), -pair[1]["tokens"], pair[0])):
            writer.writerow([
                lemma, cue, upos, entry["tokens"], len(entry["forms"]),
                "; ".join(sorted(entry["forms"])),
                "; ".join(sorted(entry["sent_ids"])[:5]),
            ])
    print(f"{len(grouped)} grupos por lema/proclítico/UPOS → {summary}")
    print(f"{len(selected)} ocorrências na lista por famílias de lemas → {shortlist}")
    print("A lista reduzida não é uma validação linguística.")
    counts = Counter(row["status"] for row in rows)
    print(f"{len(rows)} ocorrências candidatas → {output}")
    for label, count in sorted(counts.items()):
        print(f"{label}: {count}")
    print("Aviso: correspondência ortográfica não comprova segmentação.")


if __name__ == "__main__":
    main()
