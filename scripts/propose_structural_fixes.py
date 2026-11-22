#!/usr/bin/env python3
"""Propõe correções para erros estruturais do CoNLL-U — sem aplicar nada.

Gera CorBo/validation/structural_proposals.tsv com uma linha por proposta:
  prop_id, line, sent_id, kind, confidence, proposal, detail, approve
Preencha a coluna `approve` com "sim" nas linhas aceitas e rode:
  python3 scripts/apply_structural_fixes.py            # simulação
  python3 scripts/apply_structural_fixes.py --apply    # grava

Tipos de proposta
  merge          fragmento sem sent_id (bloco de tokens separado por linha em
                 branco) é unido à sentença anterior; IDs e HEADs renumerados.
                 alta  = as formas unidas reproduzem exatamente o # text anterior
                 média = reproduzem o início do # text (faltam tokens no fim)
  new_sentence   fragmento que não pertence à sentença anterior vira sentença
                 própria: sent_id = <anterior>#N, # text reconstruído das formas.
  renumber       sentença com IDs fora de sequência (sem repetição) é
                 renumerada 1..n, com HEADs remapeados.
  swapped_tokens os tokens de uma sentença reproduzem exatamente o # text de
                 outra (apenas informativo: indica onde os tokens estão).
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUT = ROOT / "CorBo/validation/structural_proposals.tsv"
P = lambda s: re.sub(r"[\s\W_]+", "", (s or "").casefold())


def parse_blocks(text):
    """Blocos separados por linha em branco, com o número da primeira linha."""
    blocks, line_no = [], 1
    for raw in text.split("\n\n"):
        lines = raw.split("\n")
        lead = 0
        while lead < len(lines) and lines[lead] == "":
            lead += 1
        if any(l.strip() for l in lines):
            blocks.append((line_no + lead, lines[lead:]))
        line_no += raw.count("\n") + 2
    return blocks


def info(lines):
    com = [l for l in lines if l.startswith("#")]
    tok = [l.split("\t") for l in lines if l and not l.startswith("#") and len(l.split("\t")) == 10]
    get = lambda k: next((re.sub(rf"^#\s*{k}\s*=\s*", "", c) for c in com if re.match(rf"#\s*{k}\s*=", c)), None)
    return get("sent_id"), get("text"), tok


def main():
    blocks = parse_blocks(CONLLU.read_text(encoding="utf-8"))
    rows, n = [], 0
    by_text = {}
    for line, lines in blocks:
        sid, text, tok = info(lines)
        if sid and text and len(P(text)) > 12:
            by_text.setdefault(P(text), sid)

    prev = None          # (sid, text, tokens acumulados, line)
    suffix = {}          # contador de novas sentenças por sid de origem
    for line, lines in blocks:
        sid, text, tok = info(lines)
        if tok and sid is None and prev and prev[0]:
            psid, ptext, ptok, _ = prev
            merged, full = P("".join(t[1] for t in ptok + tok)), P(ptext)
            forms = " ".join(t[1] for t in tok)
            if ptext and merged == full:
                kind, conf, prop = "merge", "alta", f"unir à sentença {psid}"
            elif ptext and full.startswith(merged):
                kind, conf, prop = "merge", "média", f"unir à sentença {psid} (o # text ainda tem tokens a mais no fim)"
            else:
                suffix[psid] = suffix.get(psid, 1) + 1
                new_id = f"{psid}#{suffix[psid]}"
                kind, conf, prop = "new_sentence", "média", f"criar sentença {new_id} com # text = formas"
            n += 1
            rows.append({"prop_id": f"P{n:04d}", "line": line, "sent_id": psid, "kind": kind, "confidence": conf,
                         "proposal": prop, "detail": forms[:160], "approve": ""})
            if kind == "merge":
                prev = (psid, ptext, ptok + tok, prev[3])
            continue
        if sid is not None:
            prev = (sid, text, tok, line)
            ids = [t[0] for t in tok if re.fullmatch(r"\d+", t[0])]
            if tok and ids and ids != [str(i) for i in range(1, len(ids) + 1)] and len(set(ids)) == len(ids):
                n += 1
                rows.append({"prop_id": f"P{n:04d}", "line": line, "sent_id": sid, "kind": "renumber", "confidence": "alta",
                             "proposal": "renumerar IDs 1..n e remapear HEAD", "detail": " ".join(ids[:15]), "approve": ""})
            if text and tok and P(text) != P("".join(t[1] for t in tok)):
                other = by_text.get(P("".join(t[1] for t in tok)))
                if other and other != sid:
                    n += 1
                    rows.append({"prop_id": f"P{n:04d}", "line": line, "sent_id": sid, "kind": "swapped_tokens",
                                 "confidence": "informativo", "proposal": f"os tokens reproduzem o # text de {other}",
                                 "detail": text[:160], "approve": ""})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0].keys()) if rows else ["prop_id"], delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(Counter((r["kind"], r["confidence"]) for r in rows))
    print("→", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
