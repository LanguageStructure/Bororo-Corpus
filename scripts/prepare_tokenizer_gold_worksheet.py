#!/usr/bin/env python3
"""Gera uma planilha estratificada para construir o gold de segmentação morfológica.

A amostra cruza faixa de frequência (alta ≥ 50, média 5–49, baixa 1–4) com o
estado no inventário (confirmed / proposed / unanalysed), exclui formas com
suspeita de português e pontuação, e atribui train/test de forma determinística
(50/50 por hash da forma). Para cada forma traz um exemplo do CoNLL-U com tradução.

A planilha NÃO mostra a segmentação nem o estado atribuídos pelo modelo, para não
enviesar a anotação (ver docs/tokenizer-evaluation-protocol.md). O anotador preenche:
  surface_segments  (ex.: a+ka+re; deve reconstruir a grafia)
  decision          confirmed | ambiguous | unresolved | reject
  note              (opcional; registre a representação subjacente aqui, se diferir)

Linhas com `decision` vazio são ignoradas por scripts/evaluate_tokenizer_gold.py.

Uso: python3 scripts/prepare_tokenizer_gold_worksheet.py [--n 400] [--seed 20261121]
"""
import argparse
import csv
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "docs/data/tokenizer-v5-site.json"
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUT = ROOT / "CorBo_vNext/annotations/tokenizer_gold_worksheet_v1.tsv"


def band(freq):
    return "alta" if freq >= 50 else "média" if freq >= 5 else "baixa"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20261121)
    args = ap.parse_args()
    if OUT.exists():
        raise SystemExit(f"{OUT} já existe; não sobrescrevo anotações. Apague ou renomeie antes.")

    forms = json.loads(MODEL.read_text(encoding="utf-8"))["forms"]
    cells = {}
    for form, e in forms.items():
        if e.get("lang_suspect") or not re.fullmatch(r"[a-z]+", form):
            continue
        st = e.get("review_status", "unanalysed")
        st = "proposed" if st.startswith("proposed") else st
        cells.setdefault((band(e.get("frequency", 0) or 0), st), []).append(form)

    rng = random.Random(args.seed)
    per_cell = max(1, args.n // max(1, len(cells)))
    chosen = []
    for key in sorted(cells):
        pool = sorted(cells[key])
        rng.shuffle(pool)
        chosen += [(f, key) for f in pool[:per_cell]]
    leftovers = sorted({f for v in cells.values() for f in v} - {f for f, _ in chosen})
    rng.shuffle(leftovers)
    for f in leftovers[: max(0, args.n - len(chosen))]:
        e = forms[f]
        st = e.get("review_status", "unanalysed")
        chosen.append((f, (band(e.get("frequency", 0) or 0), "proposed" if st.startswith("proposed") else st)))

    # exemplos do CoNLL-U
    wanted = {f for f, _ in chosen}
    examples, meta = {}, {}
    for line in CONLLU.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"#\s*(sent_id|text|text_por)\s*=\s*(.*)$", line)
        if m:
            if m.group(1) == "sent_id":
                meta = {}
            meta[m.group(1)] = m.group(2)
            continue
        cols = line.split("\t")
        if len(cols) == 10:
            w = cols[1].lower()
            if w in wanted and w not in examples and meta.get("text"):
                examples[w] = (meta.get("sent_id", ""), meta.get("text", ""), meta.get("text_por", ""))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["form", "surface_segments", "decision", "split", "note",
                    "frequency", "frequency_band", "example_sent_id", "example_text", "example_por"])
        for f, (b, st) in sorted(chosen):  # ordem alfabética: não revela o estrato
            split = "test" if int(hashlib.sha1(f.encode()).hexdigest(), 16) % 2 else "train"
            ex = examples.get(f, ("", "", ""))
            w.writerow([f, "", "", split, "", forms[f].get("frequency", 0), b, *ex])
    print(f"{len(chosen)} formas → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
