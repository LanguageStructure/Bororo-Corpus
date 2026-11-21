#!/usr/bin/env python3
"""Aplica ao CorBo.conllu as decisões de anotação tomadas em 21/11/2026.

Decisões (ver docs/ANNOTATION_GUIDE.md):
  1. Lema `Boe`: quando significa "os Bororo" é plural e PROPN; nas outras
     acepções é singular e NOUN. Regra mecânica aplicada só onde não há
     ambiguidade: NOUN + Number=Plur → PROPN; PROPN + Number=Sing → NOUN.
     Tokens sem Number ficam para revisão (listados no log com regra "boe_review").
  2. Sufixo -go = causativo-incoativo: Voice=CauI e Voice=IncCau → Voice=CauInc.
  3. XPOS de conjunção coordenativa unificado em `cconj` (era `conj` / `cconj`).

Cada alteração é registrada em CorBo/validation/decisions_20261121.tsv.
Idempotente quanto aos dados (rodar de novo só repete as linhas "boe_review" no log).
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
LOG = ROOT / "CorBo/validation/decisions_20261121.tsv"


def feats_dict(s):
    return dict(kv.split("=", 1) for kv in s.split("|") if "=" in kv) if s != "_" else {}


def main():
    lines = CONLLU.read_text(encoding="utf-8").split("\n")
    log, sid = [], ""
    for i, line in enumerate(lines):
        m = re.match(r"#\s*sent_id\s*=\s*(.*)$", line)
        if m:
            sid = m.group(1)
        f = line.split("\t")
        if line.startswith("#") or len(f) != 10:
            continue

        def change(col, old, new, rule):
            log.append({"line": i + 1, "sent_id": sid, "form": f[1], "column": col, "before": old, "after": new, "rule": rule})

        fd = feats_dict(f[5])
        if f[2].lower() == "boe":
            if f[3] == "NOUN" and fd.get("Number") == "Plur":
                change("UPOS", f[3], "PROPN", "boe_plural_propn")
                f[3] = "PROPN"
                if f[4] == "n":
                    change("XPOS", f[4], "propn", "boe_plural_propn")
                    f[4] = "propn"
            elif f[3] == "PROPN" and fd.get("Number") == "Sing":
                change("UPOS", f[3], "NOUN", "boe_singular_noun")
                f[3] = "NOUN"
                if f[4] == "propn":
                    change("XPOS", f[4], "n", "boe_singular_noun")
                    f[4] = "n"
            elif f[3] in ("NOUN", "PROPN") and "Number" not in fd:
                log.append({"line": i + 1, "sent_id": sid, "form": f[1], "column": "UPOS", "before": f[3],
                            "after": "(revisar: sem Number)", "rule": "boe_review"})
        if fd.get("Voice") in ("CauI", "IncCau"):
            old = f[5]
            fd["Voice"] = "CauInc"
            f[5] = "|".join(f"{k}={v}" for k, v in sorted(fd.items(), key=lambda kv: kv[0].lower()))
            change("FEATS", old, f[5], "go_cauinc")
        if f[4] == "conj":
            change("XPOS", "conj", "cconj", "xpos_cconj")
            f[4] = "cconj"
        lines[i] = "\t".join(f)

    CONLLU.write_text("\n".join(lines), encoding="utf-8")
    exists = LOG.exists()
    with open(LOG, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ["line", "sent_id", "form", "column", "before", "after", "rule"], delimiter="\t")
        if not exists:
            w.writeheader()
        w.writerows(log)
    from collections import Counter
    print(Counter(x["rule"] for x in log))


if __name__ == "__main__":
    main()
