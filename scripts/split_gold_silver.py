#!/usr/bin/env python3
"""Separa o CoNLL-U canônico em camadas gold / silver e mede a cobertura de anotação.

Definições (aplicadas sentença a sentença):
  gold   — sem `# auto_annotation`, nenhum token com `Auto=`, `AutoLowConf=` ou
           `PosMorphAnnot=AI:…` no MISC, sintaxe completa
           e nenhum erro de validação estrutural (scripts/validate_conllu.py).
  silver — sintaxe completa e nenhum erro estrutural, mas contém anotação automática.
  review — tokenizada, mas com erro estrutural ou sintaxe incompleta (lista para revisão).
  pending — unidade sem tokens (texto ainda não tokenizado).

Saídas:
  CorBo/Corpus_Files/splits/CorBo.gold.conllu
  CorBo/Corpus_Files/splits/CorBo.silver.conllu
  CorBo/Corpus_Files/splits/review_sentences.tsv
  docs/data/annotation-coverage.json   (lido pela página de cobertura do site)

O arquivo canônico não é alterado. As camadas são derivadas e reconstruíveis.
"""
import collections
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_conllu import read_blocks, validate  # noqa: E402

CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
SPLITS = ROOT / "CorBo/Corpus_Files/splits"
COVERAGE = ROOT / "docs/data/annotation-coverage.json"


AUTO_MISC = re.compile(r"(^|\|)(Auto=|AutoLowConf=|PosMorphAnnot=AI)")


def is_auto(misc):
    """Token com algum campo preenchido por modelo (Auto=, AutoLowConf=, PosMorphAnnot=AI:…)."""
    return bool(AUTO_MISC.search(misc))


def group_of(sid):
    """Grupo de proveniência derivado só do formato do sent_id (não do conteúdo)."""
    if not sid:
        return "(sem sent_id)"
    if re.match(r"^\d", sid):
        return "numérico (NNN-N)"
    m = re.match(r"^([^\W\d]+)", sid)
    return m.group(1).strip("_-") if m else sid


def main():
    issues, _ = validate(str(CONLLU))
    bad_lines = collections.defaultdict(list)
    for i in issues:
        if i["severity"] == "error":
            bad_lines[i["line"]].append(i["category"])

    SPLITS.mkdir(parents=True, exist_ok=True)
    gold, silver, review = [], [], []
    cov = collections.defaultdict(collections.Counter)

    for block in read_blocks(str(CONLLU)):
        comments = [l for _, l in block if l.startswith("#")]
        toks = [l.split("\t") for _, l in block if not l.startswith("#") and len(l.split("\t")) == 10]
        sid = next((re.sub(r"^#\s*sent_id\s*=\s*", "", c) for c in comments if re.match(r"#\s*sent_id\s*=", c)), None)
        g = group_of(sid)
        errs = sorted({c for n, _ in block for c in bad_lines.get(n, [])})
        for key in (g, "__total__"):
            cov[key]["units"] += 1
        if not toks:
            for key in (g, "__total__"):
                cov[key]["pending"] += 1
            continue
        words = [t for t in toks if re.fullmatch(r"\d+", t[0])]
        auto = any(re.match(r"#\s*auto_annotation\s*=", c) for c in comments) or any(is_auto(t[9]) for t in toks)
        full = all(t[6] != "_" and t[7] != "_" for t in words) and bool(words)
        for key in (g, "__total__"):
            c = cov[key]
            c["sentences"] += 1
            c["tokens"] += len(words)
            c["tokens_lemma"] += sum(t[2] != "_" for t in words)
            c["tokens_upos"] += sum(t[3] != "_" for t in words)
            c["tokens_feats"] += sum(t[5] != "_" for t in words)
            c["tokens_auto"] += sum(is_auto(t[9]) for t in words)
            c["sentences_full_syntax"] += full
        text = "\n".join(l for _, l in block)
        if full and not errs and sid:
            (silver if auto else gold).append(text)
            layer = "silver" if auto else "gold"
        else:
            layer = "review"
            review.append({"sent_id": sid or "", "line": block[0][0], "group": g,
                           "automatic": "yes" if auto else "no", "full_syntax": "yes" if full else "no",
                           "errors": ",".join(errs)})
        for key in (g, "__total__"):
            cov[key][layer] += 1
            if layer != "review":
                cov[key][f"tokens_{layer}"] += len(words)

    header = "# Derivado de CorBo/Corpus_Files/CorBo.conllu por scripts/split_gold_silver.py — não editar.\n"
    (SPLITS / "CorBo.gold.conllu").write_text("\n\n".join(gold) + "\n\n", encoding="utf-8")
    (SPLITS / "CorBo.silver.conllu").write_text("\n\n".join(silver) + "\n\n", encoding="utf-8")
    (SPLITS / "README.md").write_text(
        "# Camadas derivadas do CoNLL-U\n\n" + header.lstrip("# ") + "\n"
        "- `CorBo.gold.conllu`: sentenças com anotação inteiramente manual, sintaxe completa e sem erros estruturais.\n"
        "- `CorBo.silver.conllu`: sentenças estruturalmente válidas que contêm anotação automática (`Auto=`).\n"
        "- `review_sentences.tsv`: sentenças tokenizadas que precisam de revisão (erros ou sintaxe incompleta).\n\n"
        "Unidades sem tokens (pendentes de tokenização) não entram em nenhuma camada.\n", encoding="utf-8")
    with open(SPLITS / "review_sentences.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ["sent_id", "line", "group", "automatic", "full_syntax", "errors"], delimiter="\t")
        w.writeheader()
        w.writerows(review)

    def pack(c):
        t = c["tokens"] or 1
        return {"units": c["units"], "pending_tokenization": c["pending"], "sentences": c["sentences"],
                "tokens": c["tokens"], "sentences_full_syntax": c["sentences_full_syntax"],
                "gold_sentences": c["gold"], "silver_sentences": c["silver"], "review_sentences": c["review"],
                "gold_tokens": c["tokens_gold"], "silver_tokens": c["tokens_silver"],
                "pct_tokens_lemma": round(100 * c["tokens_lemma"] / t, 1),
                "pct_tokens_upos": round(100 * c["tokens_upos"] / t, 1),
                "pct_tokens_feats": round(100 * c["tokens_feats"] / t, 1),
                "pct_tokens_automatic": round(100 * c["tokens_auto"] / t, 1)}

    data = {"schema": "corbo-annotation-coverage/v1", "generated": date.today().isoformat(),
            "source": str(CONLLU.relative_to(ROOT)),
            "definitions": {"gold": "anotação manual, sintaxe completa, sem erros estruturais",
                            "silver": "estruturalmente válida, com anotação automática",
                            "review": "tokenizada, com erro estrutural ou sintaxe incompleta",
                            "pending_tokenization": "unidade documental ainda sem tokens"},
            "total": pack(cov["__total__"]),
            "groups": {k: pack(v) for k, v in sorted(cov.items(), key=lambda z: -z[1]["units"]) if k != "__total__"}}
    COVERAGE.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(data["total"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
