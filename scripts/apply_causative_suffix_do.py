#!/usr/bin/env python3
"""Causativo -do: de clítico (=do) para sufixo (-do) no Morph.

Decisão de FFG (25/11/2026): o marcador causativo -do é um sufixo do
índice pessoal, não um clítico. A segmentação dos pronomes causativos
passa de Morph=<pessoa>=do para Morph=<pessoa>-do (ex.: e=do -> e-do).

Alvo: tokens PRON com Voice=Cau cujo Morph é exatamente <pessoa>=do
(dois segmentos). Não toca outros =do, como o imperativo em a=aiwo=do.
Só muda o MISC:Morph; FORM, LEMMA, FEATS, HEAD e DEPREL ficam iguais.
Mudança por regra: não recebe Auto=.

  python3 scripts/apply_causative_suffix_do.py            # simulação
  python3 scripts/apply_causative_suffix_do.py --apply    # grava no CorBo.conllu
Depois: validate_conllu.py e split_gold_silver.py.
"""
import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo" / "Corpus_Files" / "CorBo.conllu"
LOG = ROOT / "CorBo" / "validation" / "causative_do_suffix_20261125.tsv"
GOLD = ROOT / "CorBo" / "Corpus_Files" / "splits" / "CorBo.gold.conllu"

TARGET = re.compile(r"^Morph=([a-z]+)=do$")


def gold_ids(path):
    if not path.exists():
        return set()
    return {l.split("=", 1)[1].strip() for l in path.read_text(encoding="utf-8").split("\n")
            if l.startswith("# sent_id")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="grava as mudanças no CorBo.conllu")
    ap.add_argument("--conllu", type=Path, default=CONLLU)
    args = ap.parse_args()

    gold = gold_ids(GOLD)
    lines = args.conllu.read_text(encoding="utf-8").split("\n")
    sent_id, rows = None, []
    for i, line in enumerate(lines):
        if line.startswith("# sent_id"):
            sent_id = line.split("=", 1)[1].strip()
            continue
        if not line or line.startswith("#"):
            continue
        c = line.split("\t")
        if len(c) != 10 or c[3] != "PRON" or "Voice=Cau" not in c[5].split("|"):
            continue
        misc = c[9].split("|")
        for k, item in enumerate(misc):
            m = TARGET.match(item)
            if m:
                new = f"Morph={m.group(1)}-do"
                rows.append([sent_id, c[0], c[1], item[6:], new[6:], "gold" if sent_id in gold else ""])
                misc[k] = new
                c[9] = "|".join(misc)
                lines[i] = "\t".join(c)
                break

    sents = {r[0] for r in rows}
    gold_sents = sorted({r[0] for r in rows if r[5]})
    print(f"tokens: {len(rows)} | frases: {len(sents)} | frases gold: {len(gold_sents)}")
    for g in gold_sents:
        print("  gold:", g)

    if args.apply:
        args.conllu.write_text("\n".join(lines), encoding="utf-8")
        with LOG.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["sent_id", "token_id", "form", "morph_old", "morph_new", "gold"])
            w.writerows(rows)
        print(f"gravado: {args.conllu.relative_to(ROOT)} e {LOG.relative_to(ROOT)}")
    else:
        print("simulação: nada foi gravado (use --apply)")


if __name__ == "__main__":
    main()
