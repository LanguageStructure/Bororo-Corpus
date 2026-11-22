#!/usr/bin/env python3
"""Alinha FORM e # text conforme as decisões de 22/11/2026.

1. Caixa (maiúsculas/minúsculas): quando FORM e # text diferem só na caixa,
   a grafia da fonte (# text) prevalece: o FORM recebe exatamente a caixa do
   # text. LEMMA, UPOS e as demais colunas não mudam.
2. Número de linha da fonte no início do # text ("111 Inagore Kirabodu !"):
   o número sai do # text e vai para "# source_line = 111".

Cada alteração é registrada em CorBo/validation/text_form_fixes_20261122.tsv.
  python3 scripts/fix_text_form_alignment.py           # simulação
  python3 scripts/fix_text_form_alignment.py --apply   # grava
"""
import argparse
import collections
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
LOG = ROOT / "CorBo/validation/text_form_fixes_20261122.tsv"
PUNCT = re.compile(r"[\s\"'“”‘’«»()\[\]{}.,;:!?…\-–—/]+")


def same(text, forms):
    """Texto e formas coincidem (ignorando espaços, ou pontuação)."""
    return re.sub(r"\s", "", text) == "".join(forms) or PUNCT.sub("", text) == PUNCT.sub("", " ".join(forms))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    blocks = CONLLU.read_text(encoding="utf-8").split("\n\n")
    log, stats = [], collections.Counter()
    out = []
    for b in blocks:
        lines = b.split("\n")
        ti = next((i for i, l in enumerate(lines) if re.match(r"#\s*text\s*=", l)), None)
        sid = next((re.sub(r"^#\s*sent_id\s*=\s*", "", l) for l in lines if re.match(r"#\s*sent_id\s*=", l)), "")
        toks = [(i, l.split("\t")) for i, l in enumerate(lines) if not l.startswith("#") and len(l.split("\t")) == 10
                and l.split("\t")[0].isdigit()]
        if ti is None or not toks:
            out.append(b)
            continue
        text = re.sub(r"^#\s*text\s*=\s*", "", lines[ti])
        forms = [c[1] for _, c in toks]
        if same(text, forms):
            out.append(b)
            continue

        # 2. número de linha no início do # text
        m = re.match(r"^\s*(\d+)\s*(?=\S)", text)
        if m and not forms[0].isdigit():
            rest = text[m.end():]
            if same(rest, forms) or PUNCT.sub("", rest).casefold() == PUNCT.sub("", " ".join(forms)).casefold():
                lines[ti] = "# text = " + rest
                lines.insert(ti + 1, f"# source_line = {m.group(1)}")
                log.append({"sent_id": sid, "kind": "source_line", "before": text, "after": rest})
                stats["source_line"] += 1
                text = rest
                toks = [(i + (1 if i > ti else 0), c) for i, c in toks]

        # 1. caixa: FORM recebe a caixa do # text
        if PUNCT.sub("", text).casefold() == PUNCT.sub("", " ".join(c[1] for _, c in toks)).casefold():
            low, pos, changed = text.casefold(), 0, 0
            for i, c in toks:
                f = c[1]
                if not any(ch.isalpha() for ch in f):
                    continue
                k = low.find(f.casefold(), pos)
                if k < 0 or PUNCT.sub("", text[pos:k]):  # só pontuação/espaço pode haver entre as formas
                    break
                src = text[k:k + len(f)]
                pos = k + len(f)
                if src != f and src.casefold() == f.casefold():
                    log.append({"sent_id": sid, "kind": "case", "before": f, "after": src})
                    c[1] = src
                    lines[i] = "\t".join(c)
                    changed += 1
            if changed:
                stats["case_sentences"] += 1
                stats["case_tokens"] += changed
        out.append("\n".join(lines))

    with LOG.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ["sent_id", "kind", "before", "after"], delimiter="\t")
        w.writeheader()
        w.writerows(log)
    print(dict(stats), "→", LOG.relative_to(ROOT))
    if args.apply:
        CONLLU.write_text("\n\n".join(out), encoding="utf-8")
        print("Gravado:", CONLLU.relative_to(ROOT))
    else:
        print("Simulação (use --apply para gravar).")


if __name__ == "__main__":
    main()
