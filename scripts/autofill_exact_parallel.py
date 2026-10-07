#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict
import re

PATH = Path("CorBo/Corpus_Files/CorBo.conllu")
REPORT = Path("CorBo/Corpus_Files/autofill-exact-parallel-report.tsv")

text = PATH.read_text(encoding="utf-8")
blocks = re.split(r"\n\s*\n", text)

groups = defaultdict(list)

def rows_of(block):
    return [
        line.split("\t")
        for line in block.splitlines()
        if line and not line.startswith("#") and len(line.split("\t")) == 10
    ]

def sent_id(block):
    for line in block.splitlines():
        if line.startswith("# sent_id ="):
            return line.split("=", 1)[1].strip()
    return "?"

for i, block in enumerate(blocks):
    rows = rows_of(block)
    if rows:
        key = " ".join(row[1] for row in rows)
        groups[key].append((i, sent_id(block), rows))

templates = {}

for sentence, occurrences in groups.items():
    low = sentence.lower()

    # Known cases requiring separate linguistic review.
    if "kod" in low or re.search(r"(^| )uu( |$)", low) or "itaiwore" in low:
        continue

    complete = [
        rows for _, _, rows in occurrences
        if all(
            row[2] != "_" and
            row[3] != "_" and
            row[6] != "_" and
            row[7] != "_"
            for row in rows
        )
    ]

    if not complete:
        continue

    def signature(rows):
        return [
            (row[2], row[3], row[5], row[6], row[7])
            for row in rows
        ]

    reference = signature(complete[0])

    if not all(signature(rows) == reference for rows in complete):
        continue

    templates[sentence] = complete[0]

changes = []

for sentence, occurrences in groups.items():
    if sentence not in templates:
        continue

    reference = templates[sentence]

    for block_index, sid, rows in occurrences:
        if len(rows) != len(reference):
            continue

        changed = False

        for row, ref in zip(rows, reference):
            # FORM must match exactly.
            if row[1] != ref[1]:
                continue

            # Fill only missing annotation. Never overwrite.
            for col in (2, 3, 5, 6, 7):
                if row[col] == "_" and ref[col] != "_":
                    changes.append(
                        (
                            sid,
                            row[0],
                            row[1],
                            ["ID", "FORM", "LEMMA", "UPOS", "XPOS",
                             "FEATS", "HEAD", "DEPREL"][col],
                            "_",
                            ref[col],
                            sentence,
                        )
                    )
                    row[col] = ref[col]
                    changed = True

        if changed:
            lines = blocks[block_index].splitlines()
            new_lines = []
            token_iter = iter(rows)

            for line in lines:
                if line and not line.startswith("#") and len(line.split("\t")) == 10:
                    new_lines.append("\t".join(next(token_iter)))
                else:
                    new_lines.append(line)

            blocks[block_index] = "\n".join(new_lines)

PATH.write_text("\n\n".join(blocks).rstrip() + "\n", encoding="utf-8")

with REPORT.open("w", encoding="utf-8") as f:
    f.write("sent_id\ttoken_id\tform\tfield\told\tnew\texact_parallel\n")
    for change in changes:
        f.write("\t".join(change) + "\n")

print(f"Alterações de campos: {len(changes)}")
print(f"Sentenças afetadas: {len(set(c[0] for c in changes))}")
print(f"Relatório: {REPORT}")
