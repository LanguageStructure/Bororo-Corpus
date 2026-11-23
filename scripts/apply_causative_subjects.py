#!/usr/bin/env python3
"""Corrige os sujeitos duplos em construções causativas (PRON=do).

Problema: em frases como "ure edo imaragodudo" ('ele fez eles me fazerem
trabalhar'), o causador (ure) e o causado (edo, e=do) estavam ambos como
nsubj do mesmo verbo. UD só admite um nsubj por predicado.

Regra (decisão de FFG, 23/11/2026): os índices pessoais são clíticos e
=do é o marcador causativo; a construção é monoclausal. Para cada núcleo
com dois ou mais nsubj, entre os quais pelo menos um PRON com Voice=Cau:

  * se há sujeito(s) sem =do (ex.: u=re, um SN): esse é o causador e fica
    nsubj; todos os PRON=do passam a causados;
  * se todos os sujeitos são PRON=do: o primeiro (mais à esquerda) é o
    causador mais alto e fica nsubj; os demais passam a causados.
  * causados: o mais próximo do verbo recebe iobj:agent (obl:agent se o
    núcleo já tiver iobj); os anteriores na cadeia recebem obl:agent.
  * causados cujo FORM é <lema>do recebem Morph=<lema>=do em MISC, se
    ainda não houver Morph.

Não altera: PRON=do que é o único nsubj do verbo (pode ser o próprio
causador, ex.: 1SG=CAU 3SG=CAU 3-KILL); esses vão para a lista de revisão.
Núcleos com dois sujeitos sem =do também ficam fora (outro problema).

  python3 scripts/apply_causative_subjects.py            # simulação
  python3 scripts/apply_causative_subjects.py --apply    # grava no CorBo.conllu
Depois: validate_conllu.py, split_gold_silver.py e atualizar a linha de base.
"""
import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo" / "Corpus_Files" / "CorBo.conllu"
VALID = ROOT / "CorBo" / "validation"
LOG = VALID / "causative_subjects_applied_20261123.tsv"
REVIEW = VALID / "causative_subjects_review.tsv"


def is_cau_pron(c):
    return c[3] == "PRON" and "Voice=Cau" in c[5].split("|")


def add_misc(misc, key, value):
    items = [] if misc == "_" else misc.split("|")
    if any(i.startswith(key + "=") for i in items):
        return misc
    items.insert(0, f"{key}={value}")
    return "|".join(items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="grava as mudanças no CorBo.conllu")
    ap.add_argument("--conllu", type=Path, default=CONLLU)
    args = ap.parse_args()

    lines = args.conllu.read_text(encoding="utf-8").split("\n")
    log, review = [], []

    # agrupa linhas por sentença
    i, n = 0, len(lines)
    while i < n:
        if not lines[i].strip():
            i += 1
            continue
        start = i
        while i < n and lines[i].strip():
            i += 1
        block = range(start, i)
        sid = next((lines[k].split("=", 1)[1].strip() for k in block
                    if re.match(r"#\s*sent_id\s*=", lines[k])), "?")
        text = next((lines[k].split("=", 1)[1].strip() for k in block
                     if re.match(r"#\s*text\s*=", lines[k])), "")
        toks = {}
        for k in block:
            c = lines[k].split("\t")
            if len(c) == 10 and re.fullmatch(r"\d+", c[0]):
                toks[k] = c
        subj = defaultdict(list)
        iobj_heads = set()
        for k, c in toks.items():
            if c[7] == "nsubj":
                subj[c[6]].append(k)
            if c[7].split(":")[0] == "iobj":
                iobj_heads.add(c[6])

        for head, ks in subj.items():
            cau = [k for k in ks if is_cau_pron(toks[k])]
            if not cau:
                continue
            if len(ks) == 1:
                c = toks[ks[0]]
                review.append([sid, c[0], c[1], head, "PRON=do único nsubj: causador ou causado?", text])
                continue
            plain = [k for k in ks if k not in cau]
            if len(plain) >= 2:
                review.append([sid, ",".join(toks[k][0] for k in ks), " ".join(toks[k][1] for k in ks),
                               head, "dois sujeitos sem =do além do causativo: não alterado", text])
                continue
            causees = cau if plain else cau[1:]
            causees.sort(key=lambda k: int(toks[k][0]))
            for j, k in enumerate(causees):
                c = toks[k]
                lowest = j == len(causees) - 1
                new = "iobj:agent" if lowest and head not in iobj_heads else "obl:agent"
                if new == "iobj:agent":
                    iobj_heads.add(head)
                old_deprel, old_misc = c[7], c[9]
                c[7] = new
                if c[1].lower() == c[2].lower() + "do":
                    c[9] = add_misc(c[9], "Morph", f"{c[2].lower()}=do")
                lines[k] = "\t".join(c)
                causer = toks[(plain or cau)[0]]
                log.append([sid, c[0], c[1], head, old_deprel, new, old_misc, c[9],
                            f"{causer[0]}:{causer[1]}", text])

    print(f"tokens alterados: {len(log)} | para revisão: {len(review)}")
    for row in log[:15]:
        print("  ", row[0], row[2], row[4], "->", row[5], "| causador", row[8])

    if args.apply:
        args.conllu.write_text("\n".join(lines), encoding="utf-8")
        VALID.mkdir(parents=True, exist_ok=True)
        with LOG.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["sent_id", "token", "form", "head", "deprel_antes", "deprel_depois",
                        "misc_antes", "misc_depois", "causador_mantido_nsubj", "text"])
            w.writerows(log)
        with REVIEW.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["sent_id", "token", "form", "head", "motivo", "text"])
            w.writerows(review)
        print(f"gravado: {args.conllu}\nregistro: {LOG}\nrevisão: {REVIEW}")
    else:
        print("(simulação; use --apply para gravar)")


if __name__ == "__main__":
    main()
