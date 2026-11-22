#!/usr/bin/env python3
"""Pré-calcula o resumo exibido no topo da página de estatísticas.

Saída: docs/data/statistics-summary.json
  units, tokens, types       índice documental publicado (corbo-units.json)
  collections                unidades e tokens por coleção
  conllu                     sentenças, tokens, gold/silver (annotation-coverage.json)
  upos                       distribuição de classes no CoNLL-U
Assim a página mostra os números sem calcular tudo no navegador.
"""
import collections
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data"
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?")


def main():
    units = json.loads((DATA / "corbo-units.json").read_text(encoding="utf-8"))
    coll = collections.defaultdict(lambda: [0, 0])
    grp = collections.defaultdict(lambda: [0, 0])
    types, tokens = set(), 0
    for u in units:
        ws = [w.casefold() for w in WORD.findall(u.get("b") or "")]
        tokens += len(ws)
        types.update(ws)
        c = coll[u.get("collection") or "Sem coleção"]
        c[0] += 1
        c[1] += len(ws)
        g = grp[u.get("group") or "Outros"]
        g[0] += 1
        g[1] += len(ws)
    upos = collections.Counter()
    for line in (ROOT / "CorBo/Corpus_Files/CorBo.conllu").read_text(encoding="utf-8").split("\n"):
        f = line.split("\t")
        if len(f) == 10 and f[0].isdigit() and f[3] not in ("_", "PUNCT"):
            upos[f[3]] += 1
    cov = {}
    cp = DATA / "annotation-coverage.json"
    if cp.exists():
        cov = json.loads(cp.read_text(encoding="utf-8")).get("total", {})
    # Totais oficiais: os mesmos de corbo-stats.json (página inicial), para os números coincidirem.
    sp = DATA / "corbo-stats.json"
    st = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    out = {
        "generated": date.today().isoformat(),
        "units": st.get("units", len(units)), "tokens": st.get("tokens", tokens), "types": st.get("types", len(types)),
        "collections": sorted(([k, v[0], v[1]] for k, v in coll.items()), key=lambda x: -x[2]),
        "groups": sorted(([k, v[0], v[1]] for k, v in grp.items()), key=lambda x: -x[2]),
        "conllu": {k: cov.get(k) for k in ("sentences", "tokens", "gold_sentences", "silver_sentences",
                                           "review_sentences", "pending_tokenization", "pct_tokens_automatic")},
        "upos": upos.most_common(),
    }
    (DATA / "statistics-summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{out['units']} unidades, {out['tokens']} tokens, {out['types']} formas, {len(out['collections'])} coleções")


if __name__ == "__main__":
    main()
