#!/usr/bin/env python3
"""Planilha de revisão das sentenças em que o # text e os tokens divergem.

Para cada sentença com erro text_form_mismatch em CorBo/validation/issues.tsv,
mostra o texto, os tokens e as diferenças (tokens → texto), classificadas em:
  texto_tem_mais    há no texto material sem token (palavra, sílaba, pontuação)
  tokens_tem_mais   há token sem correspondente no texto
  grafia_diferente  token e texto escrevem a mesma posição de modo diferente
  fusao_ou_divisao  o token junta palavras do texto ou divide uma palavra
Coluna "decisao" para preencher: texto (corrigir os tokens pelo texto),
tokens (corrigir o texto pelos tokens) ou ok (registrar como divergência aceita).

  python3 scripts/text_token_worksheet.py   # grava CorBo/validation/texto_tokens_revisao.tsv
"""
import collections
import csv
import difflib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
ISSUES = ROOT / "CorBo/validation/issues.tsv"
OUT = ROOT / "CorBo/validation/texto_tokens_revisao.tsv"
QUOTES = "\"'‘’“”«»"


def blocks():
    for raw in CONLLU.read_text(encoding="utf-8").split("\n\n"):
        lines = raw.strip("\n").split("\n")
        sid = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("# sent_id")), None)
        text = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("# text =")), "")
        forms = [l.split("\t")[1] for l in lines if l and l[0].isdigit() and "\t" in l]
        if sid:
            yield sid, text, forms


def classify(text, forms):
    t = [w for w in re.findall(r"\w+|[^\w\s]+", "".join(ch for ch in text if ch not in QUOTES))]
    f = [w for w in forms if w not in QUOTES]
    kinds, diffs = set(), []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, f, t, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        a, b = " ".join(f[i1:i2]), " ".join(t[j1:j2])
        diffs.append(f"[{a}]→[{b}]")
        if op == "insert":
            kinds.add("texto_tem_mais")
        elif op == "delete":
            kinds.add("tokens_tem_mais")
        elif a.replace(" ", "").lower() == b.replace(" ", "").lower():
            kinds.add("fusao_ou_divisao")
        else:
            kinds.add("grafia_diferente")
    return "+".join(sorted(kinds)) or "pontuacao", "; ".join(diffs)


def main():
    with ISSUES.open(encoding="utf-8") as fh:
        ids = {r["sent_id"] for r in csv.DictReader(fh, delimiter="\t") if r["category"] == "text_form_mismatch"}
    prev = {}
    if OUT.exists():
        with OUT.open(encoding="utf-8") as fh:
            prev = {r["sent_id"]: (r["decisao"], r["observacao"]) for r in csv.DictReader(fh, delimiter="\t")}
    rows = []
    for sid, text, forms in blocks():
        if sid in ids:
            kind, diffs = classify(text, forms)
            d, o = prev.get(sid, ("", ""))
            rows.append([sid, kind, diffs, text, " ".join(forms), d, o])
    rows.sort(key=lambda r: (r[1], r[0]))
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["sent_id", "tipo", "diferencas_tokens_para_texto", "text", "tokens", "decisao", "observacao"])
        w.writerows(rows)
    print(collections.Counter(r[1] for r in rows).most_common(), "→", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
