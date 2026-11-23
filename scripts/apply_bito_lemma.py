#!/usr/bin/env python3
"""Corrige o paradigma de *bito* 'matar' (decisão de FFG, 23/11/2026).

*bito* é um verbo transitivo; o *-to* não é causativo. Para tokens VERB cuja
forma é *bito* ou <índice>+*wido* (iwido, awido, ewido, cewido, pawido, tawido):
  * LEMMA passa a bito;
  * Voice=Cau é retirado de FEATS;
  * Morph=e=bi=to (análise antiga) passa a e=bito.
Formas de *bi* 'morrer' (bire, ewire, bikare, ...) não são tocadas.
Formas derivadas (bitodure, ewidodu, Voice=CauPass) ficam na lista de revisão.

  python3 scripts/apply_bito_lemma.py            # simulação
  python3 scripts/apply_bito_lemma.py --apply    # grava no CorBo.conllu
"""
import argparse, csv, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo" / "Corpus_Files" / "CorBo.conllu"
LOG = ROOT / "CorBo" / "validation" / "bito_lemma_applied_20261123.tsv"
REVIEW = ROOT / "CorBo" / "validation" / "bito_lemma_review.tsv"
PARADIGM = re.compile(r"^(bito|(i|a|e|ce|pa|ta)wido)$")
DERIVED = re.compile(r"^(bito|(i|a|e|ce|pa|ta)wido)\w+$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--conllu", type=Path, default=CONLLU)
    a = ap.parse_args()
    lines = a.conllu.read_text(encoding="utf-8").split("\n")
    log, review, sid = [], [], "?"
    for k, line in enumerate(lines):
        if re.match(r"#\s*sent_id\s*=", line):
            sid = line.split("=", 1)[1].strip()
        c = line.split("\t")
        if len(c) != 10 or not re.fullmatch(r"\d+", c[0]):
            continue
        f = c[1].lower()
        if c[3] == "VERB" and PARADIGM.match(f):
            old = list(c)
            c[2] = "bito"
            feats = [x for x in c[5].split("|") if x not in ("Voice=Cau", "_")]
            c[5] = "|".join(feats) if feats else "_"
            c[9] = c[9].replace("Morph=e=bi=to", "Morph=e=bito")
            if c != old:
                lines[k] = "\t".join(c)
                log.append([sid, c[0], c[1], old[2], c[2], old[5], c[5], old[9], c[9]])
        elif DERIVED.match(f) or (f.startswith("bito") and c[2].lower() != "bito"):
            review.append([sid, c[0], c[1], c[2], c[3], c[5], "forma derivada de bito: conferir lema e Voice"])
    print(f"tokens alterados: {len(log)} | para revisão: {len(review)}")
    from collections import Counter
    print(Counter((r[2].lower(), r[3], r[5]) for r in log).most_common(20))
    if a.apply:
        a.conllu.write_text("\n".join(lines), encoding="utf-8")
        for path, head, rows in ((LOG, ["sent_id", "token", "form", "lemma_antes", "lemma_depois", "feats_antes", "feats_depois", "misc_antes", "misc_depois"], log),
                                 (REVIEW, ["sent_id", "token", "form", "lemma", "upos", "feats", "motivo"], review)):
            with path.open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh, delimiter="\t"); w.writerow(head); w.writerows(rows)
        print("gravado; registro:", LOG.name, "| revisão:", REVIEW.name)
    else:
        print("(simulação; use --apply para gravar)")
        for r in review[:20]: print("  revisão:", r[2], r[3], r[4], r[5])


if __name__ == "__main__":
    main()
