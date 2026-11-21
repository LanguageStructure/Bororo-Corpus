#!/usr/bin/env python3
"""Compara a segmentação do tokenizador CorBo com Morfessor e SentencePiece.

Pré-requisitos:
  pip install morfessor sentencepiece
  planilha gold anotada: CorBo_vNext/annotations/tokenizer_gold_worksheet_v1.tsv
  (colunas surface_segments e decision preenchidas; ver docs/TOKENIZER.md)

Procedimento:
  1. Treino não supervisionado com as palavras dos textos publicados
     (docs/data/corbo-units.json), com e sem os textos bíblicos (--sem-biblicos).
  2. Avaliação só no split "test" da planilha, decisões confirmed/ambiguous
     (para ambiguous vale qualquer análise aceita). Entradas "reject" contam como
     negativas: o método não deve reproduzir a segmentação rejeitada.
  3. Métricas: precisão, cobertura e F1 de fronteiras; acerto exato por palavra;
     resultados por faixa de frequência.

Saída: relatório Markdown (padrão: CorBo/validation/segmenter_comparison.md) e JSON.

Uso:
  python3 scripts/compare_segmenters.py
  python3 scripts/compare_segmenters.py --sem-biblicos --vocab 1000 4000
"""
import argparse
import collections
import csv
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "CorBo_vNext/annotations/tokenizer_gold_worksheet_v1.tsv"
UNITS = ROOT / "docs/data/corbo-units.json"
V5 = ROOT / "docs/data/tokenizer-v5-site.json"
WORD = re.compile(r"[^\W\d_]+")
BIBLICAL = {"Novo Testamento", "Antigo Testamento", "Textos bíblicos"}


def boundaries(segs):
    out, at = set(), 0
    for s in segs[:-1]:
        at += len(s)
        out.add(at)
    return out


def read_gold():
    gold = collections.defaultdict(list)
    meta = {}
    with GOLD.open(encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            dec = (r.get("decision") or "").strip().casefold()
            if r.get("split", "").strip() != "test" or dec not in {"confirmed", "ambiguous", "reject"}:
                continue
            form = r["form"].strip().casefold()
            segs = [x.strip().casefold() for x in r["surface_segments"].split("+") if x.strip()]
            if "".join(segs) != form:
                continue
            gold[form].append((dec, tuple(segs)))
            meta[form] = r.get("frequency_band", "")
    return gold, meta


def corpus_words(skip_biblical):
    counts = collections.Counter()
    for u in json.loads(UNITS.read_text(encoding="utf-8")):
        if skip_biblical and u.get("group") in BIBLICAL:
            continue
        counts.update(w.casefold() for w in WORD.findall(u.get("b") or ""))
    return counts


def corbo_segmenter():
    forms = json.loads(V5.read_text(encoding="utf-8"))["forms"]

    def seg(w):
        e = forms.get(w)
        if e:
            for a in e.get("analyses", []):
                s = a.get("surface_segments") or (a.get("segments") if a.get("concatenative", True) else None)
                if s and len(s) > 1 and "".join(s) == w:
                    return list(s)
        return [w]
    return seg


def morfessor_segmenter(counts):
    import morfessor
    model = morfessor.BaselineModel()
    model.load_data([(c, w) for w, c in counts.items()], count_modifier=lambda x: 1)  # treino por tipo
    model.train_batch()
    return lambda w: list(model.viterbi_segment(w)[0])


def sentencepiece_segmenter(counts, vocab, kind):
    import sentencepiece as spm
    tmp = Path(tempfile.mkdtemp())
    (tmp / "words.txt").write_text("\n".join(w for w, c in counts.items() for _ in range(min(c, 20))), encoding="utf-8")
    prefix = str(tmp / f"sp_{kind}_{vocab}")
    spm.SentencePieceTrainer.train(input=str(tmp / "words.txt"), model_prefix=prefix, vocab_size=vocab, model_type=kind,
                                   character_coverage=1.0, hard_vocab_limit=False, minloglevel=2)
    sp = spm.SentencePieceProcessor(model_file=prefix + ".model")

    def seg(w):
        pieces = [p.replace("▁", "") for p in sp.encode(w, out_type=str)]
        pieces = [p for p in pieces if p]
        return pieces if "".join(pieces) == w else [w]
    return seg


def evaluate(seg, gold, meta):
    tp = fp = fn = exact = n = rej_hit = rej_n = 0
    by_band = collections.defaultdict(lambda: [0, 0])
    for form, entries in gold.items():
        pred = tuple(seg(form))
        pb = boundaries(pred)
        accepted = [s for d, s in entries if d in ("confirmed", "ambiguous")]
        rejected = [s for d, s in entries if d == "reject"]
        if rejected:
            rej_n += 1
            rej_hit += pred in rejected
        if not accepted:
            continue
        best = max(accepted, key=lambda s: len(pb & boundaries(s)) - len(pb ^ boundaries(s)))
        gb = boundaries(best)
        tp += len(pb & gb); fp += len(pb - gb); fn += len(gb - pb)
        ok = pred in accepted
        exact += ok; n += 1
        by_band[meta.get(form, "")][0] += ok
        by_band[meta.get(form, "")][1] += 1
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": p, "recall": r, "f1": f, "exact": exact / n if n else 0.0, "n": n,
            "rejected_reproduced": rej_hit, "rejected_total": rej_n,
            "by_band": {k: v[0] / v[1] for k, v in by_band.items() if v[1]}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sem-biblicos", action="store_true", help="treinar sem os textos bíblicos")
    ap.add_argument("--vocab", type=int, nargs="+", default=[1000, 4000], help="tamanhos de vocabulário do SentencePiece")
    ap.add_argument("--out", default=str(ROOT / "CorBo/validation/segmenter_comparison.md"))
    args = ap.parse_args()

    gold, meta = read_gold()
    if not gold:
        raise SystemExit("A planilha gold ainda não tem entradas de teste anotadas (decision vazio).")
    counts = corpus_words(args.sem_biblicos)
    systems = {"CorBo v5": corbo_segmenter(), "Sem segmentação (linha de base)": lambda w: [w]}
    try:
        systems["Morfessor Baseline"] = morfessor_segmenter(counts)
    except ImportError:
        print("morfessor não instalado: pip install morfessor")
    try:
        for v in args.vocab:
            for kind in ("unigram", "bpe"):
                systems[f"SentencePiece {kind} {v}"] = sentencepiece_segmenter(counts, v, kind)
    except ImportError:
        print("sentencepiece não instalado: pip install sentencepiece")

    results = {name: evaluate(seg, gold, meta) for name, seg in systems.items()}
    pct = lambda x: f"{100 * x:.1f}%"
    lines = ["# Comparação de segmentadores", "",
             f"Gold: {sum(1 for _ in gold)} formas do split de teste · treino {'sem' if args.sem_biblicos else 'com'} textos bíblicos "
             f"({len(counts):,} tipos).", "",
             "| Sistema | Precisão | Cobertura | F1 (fronteiras) | Acerto exato | Segmentações rejeitadas reproduzidas |",
             "|---|---:|---:|---:|---:|---:|"]
    for name, r in sorted(results.items(), key=lambda x: -x[1]["f1"]):
        lines.append(f"| {name} | {pct(r['precision'])} | {pct(r['recall'])} | {pct(r['f1'])} | {pct(r['exact'])} | "
                     f"{r['rejected_reproduced']}/{r['rejected_total']} |")
    lines += ["", "Acerto exato por faixa de frequência:", ""]
    bands = sorted({b for r in results.values() for b in r["by_band"]})
    lines += ["| Sistema | " + " | ".join(bands) + " |", "|---|" + "---:|" * len(bands)]
    for name, r in results.items():
        lines.append(f"| {name} | " + " | ".join(pct(r["by_band"].get(b, 0)) for b in bands) + " |")
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path(args.out).with_suffix(".json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
