#!/usr/bin/env python3
"""Lista para revisão os acentos gráficos em palavras Bororo.

Regra (FFG, 22/11/2026): em Bororo só se acentuam oxítonas de duas ou mais
sílabas. O acento é significativo e fica no FORM. A lista aponta:
  monossilabo_acentuado  forma de uma sílaba com acento (contraria a regra)
  acento_nao_final       acento fora da última vogal (contraria a regra)
  oxitona_sem_acento     forma sem acento cuja versão acentuada (oxítona) também
                         ocorre: pode ser grafia sem o acento devido, ou palavra
                         diferente (paroxítona)
Palavras portuguesas (letras fora do inventário Bororo, ã, õ, ç) ficam de fora;
as que só usam letras do inventário (é, já, cá, tá, pátio…) são marcadas na coluna nota.
Sílabas são contadas pelas vogais escritas (aproximação).

  python3 scripts/review_accents.py   # grava CorBo/validation/acentos_revisao.tsv
"""
import collections
import csv
import re
import unicodedata as ud
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUT = ROOT / "CorBo/validation/acentos_revisao.tsv"
BORORO = set("aeioubcdgjkmnprtw")
VOW = "aeiou"
# palavras portuguesas com grafia só de letras do inventário Bororo (ficam na lista, marcadas)
PORTUGUES = {"abóbora", "bóbora", "cemitério", "córrego", "egídio", "eugênio", "negócio", "pátio",
             "índio", "né", "já", "dá", "é", "aí", "cá", "tá", "pá"}


def base(s):
    return "".join(ch for ch in ud.normalize("NFD", s) if not ud.combining(ch))


def is_bororo(form):
    return set(base(form.lower())) <= BORORO and not re.search("[ãõç]", form.lower())


def main():
    occ = collections.defaultdict(lambda: {"n": 0, "lemmas": collections.Counter(), "upos": collections.Counter(), "ex": []})
    for block in CONLLU.read_text(encoding="utf-8").split("\n\n"):
        sid = next((l.split("=", 1)[1].strip() for l in block.split("\n") if l.startswith("# sent_id")), "")
        for l in block.split("\n"):
            c = l.split("\t")
            if len(c) != 10 or not c[0].isdigit() or not re.search(r"[a-zA-Z]", base(c[1])):
                continue
            f = c[1].lower()
            o = occ[f]
            o["n"] += 1
            o["lemmas"][c[2]] += 1
            o["upos"][c[3]] += 1
            if len(o["ex"]) < 3:
                o["ex"].append(sid)
    accented = {f for f in occ if base(f) != f and is_bororo(f)}
    rows = []
    for f in sorted(accented):
        b = base(f)
        nv = sum(ch in VOW for ch in b)
        last = max(i for i, ch in enumerate(b) if ch in VOW)
        acc = [i for i, ch in enumerate(ud.normalize("NFC", f)) if base(ch) != ch]
        if nv < 2:
            kind = "monossilabo_acentuado"
        elif acc and acc[-1] != last:
            kind = "acento_nao_final"
        else:
            kind = None
        o = occ[f]
        if kind:
            rows.append([kind, f, o["n"], b, occ[b]["n"] if b in occ else 0,
                         ",".join(l for l, _ in o["lemmas"].most_common(3)),
                         ",".join(u for u, _ in o["upos"].most_common(2)), " ".join(o["ex"])])
        if b in occ and nv >= 2 and not kind:
            ob = occ[b]
            rows.append(["oxitona_sem_acento", b, ob["n"], f, o["n"],
                         ",".join(l for l, _ in ob["lemmas"].most_common(3)),
                         ",".join(u for u, _ in ob["upos"].most_common(2)), " ".join(ob["ex"])])
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["tipo", "forma", "ocorrencias", "forma_alternativa", "ocorrencias_alternativa",
                     "lemas", "upos", "exemplos", "nota", "decisao"])
        w.writerows(r + ["possivelmente português" if (r[1] in PORTUGUES or r[3] in PORTUGUES) else "", ""] for r in rows)
    print(collections.Counter(r[0] for r in rows), "→", OUT.relative_to(ROOT))
    for r in rows:
        print("  ", r[0], r[1], r[2], "|", r[3], r[4])


if __name__ == "__main__":
    main()
