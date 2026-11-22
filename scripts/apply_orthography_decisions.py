#!/usr/bin/env python3
"""Decisões de 22/11/2026 (ver docs/ORTOGRAFIA.md e docs/ANNOTATION_GUIDE.md).

1. Boe/boe pela caixa: FORM "Boe" = PROPN, XPOS propn, lema Boe, Number=Plur;
   FORM "boe" = NOUN, XPOS n, lema boe, Number=Sing. Os outros traços são mantidos
   (PronType e Mood, que não cabem em nome, são removidos). Tokens cujo lema
   aponta outra palavra (erro de tokenização) ficam para revisão.
2. Reticências: cada token de pontos passa a reproduzir o # text (".." no texto
   = token "..", não "..."), e pontos seguidos sem espaço entre si formam um só
   token; "!.." vira "!" + "..". O alinhamento é feito caractere a caractere
   (aspas ignoradas); os HEADs são remapeados. Casos sem alinhamento claro ficam
   no registro para revisão.

  python3 scripts/apply_orthography_decisions.py           # simulação
  python3 scripts/apply_orthography_decisions.py --apply   # grava e registra em CorBo/validation/
"""
import argparse
import collections
import csv
import difflib
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
DROP = ("PronType", "Mood")


def feats_set(feats, number):
    d = {} if feats in ("_", "") else dict(f.split("=", 1) for f in feats.split("|") if "=" in f)
    for k in DROP:
        d.pop(k, None)
    d["Number"] = number
    return "|".join(f"{k}={d[k]}" for k in sorted(d, key=str.lower))


def fix_boe(c):
    form = c[1]
    if form not in ("Boe", "boe") or c[2] not in ("Boe", "boe", "_"):
        return None
    new = list(c)
    if form == "Boe":
        new[2], new[3], new[4], new[5] = "Boe", "PROPN", "propn", feats_set(c[5], "Plur")
    else:
        new[2], new[3], new[4], new[5] = "boe", "NOUN", "n", feats_set(c[5], "Sing")
    return new if new != c else None


QUOTES = "\"'‘’“”«»"


def dot_spans(text, toks):
    """Alinha caractere a caractere as formas ao # text (sem aspas) e devolve, para
    cada token só de pontos, o trecho do texto que lhe corresponde: (início, fim, pontos)
    ou None. Pontos do texto sem token são dados ao token de pontos vizinho."""
    t = "".join(ch for ch in text if ch not in QUOTES)
    forms = [c[1] for c in toks]
    f = "".join(forms)
    owner = [k for k, x in enumerate(forms) for _ in x]  # token de cada caractere de f
    ti_of = [None] * len(f)
    extra = []  # (posição no texto, token vizinho anterior, seguinte)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, f, t, autojunk=False).get_opcodes():
        if op in ("equal", "replace"):
            for d in range(min(i2 - i1, j2 - j1)):
                ti_of[i1 + d] = j1 + d
        if op == "insert" or (op == "replace" and j2 - j1 > i2 - i1):
            j0 = j1 + (0 if op == "insert" else i2 - i1)
            prev = owner[i2 - 1] if i2 > 0 else None
            nxt = owner[i2] if i2 < len(f) else None
            extra.extend((j, prev, nxt) for j in range(j0, j2))
    spans = {}
    for k, form in enumerate(forms):
        if not re.fullmatch(r"\.+", form):
            continue
        idx = [ti_of[i] for i in range(len(f)) if owner[i] == k and ti_of[i] is not None and t[ti_of[i]] == "."]
        for j, prev, nxt in extra:
            if t[j] == "." and (prev == k or (nxt == k and not (prev is not None and re.fullmatch(r"\.+", forms[prev])))):
                idx.append(j)
        idx = sorted(set(idx))
        runs = []
        for j in idx:  # trechos contíguos de pontos (".. ." = dois trechos)
            if runs and j == runs[-1][1]:
                runs[-1][1] = j + 1
            else:
                runs.append([j, j + 1])
        if runs and all(not t[a:b].strip(".") for a, b in runs) \
                and all(not t[runs[r][1]:runs[r + 1][0]].strip() for r in range(len(runs) - 1)):
            spans[k] = [tuple(r) for r in runs]
    return t, spans


def merge_dots(text, toks):
    """Faz cada token de pontos reproduzir o # text e une pontos contíguos.
    Devolve a nova lista de colunas, ou None se nada mudar."""
    t, spans = dot_spans(text, toks)
    if not spans:
        return None
    # 1) cada token de pontos vira um ou mais trechos do texto
    items = []  # (colunas, trecho, id original de que herda o HEAD, é cópia?)
    for k, c in enumerate(toks):
        if k in spans:
            for r, sp in enumerate(spans[k]):
                items.append((c, sp, c[0], r > 0))
        else:
            items.append((c, None, c[0], False))
    # 2) trechos contíguos se unem
    groups, i = [], 0
    while i < len(items):
        j = i
        while items[i][1] and j + 1 < len(items) and items[j + 1][1] and items[j + 1][1][0] == items[j][1][1]:
            j += 1
        groups.append((i, j))
        i = j + 1
    newid = {}
    for n, (a, b) in enumerate(groups, 1):
        for k in range(a, b + 1):
            if not items[k][3]:
                newid.setdefault(items[k][2], str(n))
    out = []
    for n, (a, b) in enumerate(groups, 1):
        c, sp, _, copy = items[a]
        c = list(c)
        if copy:  # ponto que estava fundido num token anterior: depende do mesmo HEAD, como punct
            c[5], c[8], c[9] = "_", "_", "_"
            c[7] = "punct" if c[6] != "_" else "_"
        c[0] = str(n)
        if sp:
            c[1] = c[2] = t[sp[0]:items[b][1][1]]
        if c[6] not in ("_", "0"):
            c[6] = newid.get(c[6], "_")
            if c[6] in ("_", str(n)):  # HEAD inexistente ou dentro do próprio grupo de pontos
                c[6], c[7] = "_", "_"
        out.append(c)
    return None if [x[:3] for x in out] == [x[:3] for x in toks] else out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    raw = CONLLU.read_text(encoding="utf-8").rstrip("\n").split("\n\n")
    log, stats, skipped = [], collections.Counter(), []
    for bi, block in enumerate(raw):
        lines = block.strip("\n").split("\n")
        sid = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("# sent_id")), "")
        text = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("# text =")), "")
        com = [l for l in lines if l.startswith("#")]
        tok = [l.split("\t") for l in lines if l and not l.startswith("#")]
        if any(len(c) != 10 or not c[0].isdigit() for c in tok):
            continue
        changed = False
        for k, c in enumerate(tok):
            n = fix_boe(c)
            if n:
                log.append([sid, c[0], "boe", "\t".join(c[1:6]), "\t".join(n[1:6])])
                stats["boe"] += 1
                tok[k] = n
                changed = True
            elif c[1] in ("Boe", "boe") and c[2] not in ("Boe", "boe", "_"):
                skipped.append([sid, c[0], "boe_lema_divergente", "\t".join(c[1:6]), ""])
        if any(re.fullmatch(r"\.+", c[1]) for c in tok) or ".." in text:
            m = merge_dots(text, tok)
            if m is not None:
                merged = len(tok) - len(m)
                log.append([sid, "", "reticencias", " ".join(c[1] for c in tok if set(c[1]) == {"."}),
                            " ".join(c[1] for c in m if set(c[1]) == {"."})])
                stats["reticencias_sentencas"] += 1
                stats["saldo_de_tokens"] -= merged
                tok = m
                changed = True
            elif re.search(r"\.\.", text) and re.findall(r"\.+", "".join(ch for ch in text if ch not in QUOTES)) \
                    != [c[1] for c in tok if re.fullmatch(r"\.+", c[1])]:
                skipped.append([sid, "", "reticencias_sem_alinhamento", text[:100], ""])
        if changed:
            raw[bi] = "\n".join(com + ["\t".join(c) for c in tok])
    print(dict(stats), f"; {len(skipped)} casos deixados para revisão")
    if a.apply:
        CONLLU.write_text("\n\n".join(raw) + "\n\n", encoding="utf-8")
        p = ROOT / f"CorBo/validation/orthography_fixes_{date.today():%Y%m%d}.tsv"
        with p.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(["sent_id", "token", "kind", "before", "after"])
            w.writerows(log + skipped)
        print("registro:", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
