#!/usr/bin/env python3
"""Segunda rodada de propostas de correção do CoNLL-U: IDs, raiz e UPOS.

Gera CorBo/validation/tree_proposals.tsv com uma linha por sentença ou token.
Tipos de proposta:
  renumber_ids  IDs repetidos ou fora de ordem são renumerados 1..n; cada HEAD
                é remapeado para o token a que apontava. Quando um HEAD aponta
                para um ID repetido e não dá para saber qual dos dois, ele vira
                "_" (confiança média).
  set_root      a sentença tem um único token com HEAD=0, mas o DEPREL dele
                não é "root": o DEPREL passa a "root". Confiança alta só se esse
                token é verbo ou a frase tem até duas palavras ("Ca !").
  reroot        o token com HEAD=0 não é verbo, e um verbo depende dele: o
                verbo vira a raiz e o token antigo passa a depender do verbo.
  fill_upos     UPOS "_" é preenchido quando a mesma forma tem um UPOS
                dominante (>= 90%, >= 3 ocorrências) no resto do corpus;
                o token recebe Auto=upos no MISC.
Problemas sem correção automática (ciclos, traços malformados, etc.) vão para
CorBo/validation/manual_review.tsv.

  python3 scripts/propose_tree_fixes.py                 # gera as propostas
  python3 scripts/propose_tree_fixes.py --apply         # aplica approve=sim
  python3 scripts/propose_tree_fixes.py --apply --alta  # aplica também todas as de confiança alta
Depois: validate_conllu.py, split_gold_silver.py e atualizar a linha de base.
"""
import argparse
import collections
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUT = ROOT / "CorBo/validation/tree_proposals.tsv"
MANUAL = ROOT / "CorBo/validation/manual_review.tsv"
ISSUES = ROOT / "CorBo/validation/issues.tsv"
FIELDS = ["prop_id", "sent_id", "kind", "confidence", "proposal", "detail", "approve"]
VERB_CHILD = {"parataxis", "ccomp", "conj", "advcl", "appos", "flat", "dep", "xcomp", "csubj"}
OLD_TO_NEW_DEPREL = {"PUNCT": "punct", "ADV": "advmod", "PRON": "nsubj", "CCONJ": "cc",
                     "SCONJ": "mark", "INTJ": "discourse", "PART": "discourse", "AUX": "aux"}


def read_blocks():
    out = []
    for raw in CONLLU.read_text(encoding="utf-8").rstrip("\n").split("\n\n"):
        lines = raw.strip("\n").split("\n")
        sid = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("# sent_id")), None)
        out.append([sid, lines])
    return out


def toks_of(lines):
    return [(i, l.split("\t")) for i, l in enumerate(lines)
            if l and not l.startswith("#") and len(l.split("\t")) == 10 and l.split("\t")[0].isdigit()]


def add_misc(misc, item):
    return item if misc in ("_", "") else misc + "|" + item


def renumber_plan(toks):
    ids = [c[0] for _, c in toks]
    if ids == [str(k) for k in range(1, len(ids) + 1)]:
        return None
    cnt = collections.Counter(ids)
    first = {}
    for pos, (_, c) in enumerate(toks):
        first.setdefault(c[0], []).append(pos)
    newheads, ambiguous = [], 0
    for pos, (_, c) in enumerate(toks):
        h = c[6]
        if h in ("_", "0"):
            newheads.append(h)
            continue
        cands = first.get(h, [])
        if len(cands) > 1:
            # o token "inserido" (Morph=, sem HEAD) é o candidato menos provável
            real = [p for p in cands if not (toks[p][1][6] == "_" and "Morph=" in toks[p][1][9])]
            cands = real if len(real) == 1 else cands
        if len(cands) == 1 and cands[0] != pos:
            newheads.append(str(cands[0] + 1))
        else:
            newheads.append("_")
            ambiguous += 1
    has_tree = any(c[6] not in ("_",) for _, c in toks)
    conf = "alta" if ambiguous == 0 else "média"
    return {"newheads": newheads, "ambiguous": ambiguous, "has_tree": has_tree, "conf": conf,
            "dups": sum(v - 1 for v in cnt.values())}


def root_plan(toks):
    if any(c[6] == "_" for _, c in toks):
        return None
    zero = [(p, c) for p, (_, c) in enumerate(toks) if c[6] == "0"]
    if len(zero) != 1 or zero[0][1][7] == "root":
        return None
    p, r = zero[0]
    if r[3] == "PUNCT":
        return None
    kids = [(q, c) for q, (_, c) in enumerate(toks) if c[6] == r[0] and c[3] == "VERB" and c[7] in VERB_CHILD]
    if r[3] not in ("VERB", "AUX") and kids:
        q, v = kids[0]
        return {"kind": "reroot", "conf": "média", "root": p, "verb": q,
                "proposal": f"{v[1]} (token {v[0]}) vira raiz; {r[1]} (token {r[0]}) passa a {OLD_TO_NEW_DEPREL.get(r[3], r[7])} de {v[1]}"}
    content = sum(1 for _, c in toks if c[3] != "PUNCT")
    conf = "alta" if r[3] in ("VERB", "AUX") or content <= 2 else "média"
    return {"kind": "set_root", "conf": conf, "root": p,
            "proposal": f"DEPREL de {r[1]} (token {r[0]}): {r[7]} → root"}


def upos_table(blocks):
    tab = collections.defaultdict(collections.Counter)
    for _, lines in blocks:
        for _, c in toks_of(lines):
            if c[3] != "_":
                tab[c[1].lower()][c[3]] += 1
    return tab


def propose():
    blocks = read_blocks()
    tab = upos_table(blocks)
    rows, n = [], 0
    def add(sid, kind, conf, prop, detail):
        nonlocal n
        n += 1
        rows.append({"prop_id": f"T{n:04d}", "sent_id": sid, "kind": kind, "confidence": conf,
                     "proposal": prop, "detail": detail, "approve": ""})
    for sid, lines in blocks:
        toks = toks_of(lines)
        if not toks or sid is None:
            continue
        text = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("# text =")), "")
        rp = renumber_plan(toks)
        if rp:
            what = f"{rp['dups']} ID(s) repetido(s); " if rp["dups"] else "IDs fora de ordem; "
            what += "sem árvore" if not rp["has_tree"] else (
                "HEADs remapeados" if not rp["ambiguous"] else f"{rp['ambiguous']} HEAD(s) ambíguo(s) viram _")
            add(sid, "renumber_ids", rp["conf"], "renumerar 1..n; " + what, text[:120])
        else:  # a raiz de frases renumeradas é avaliada na rodada seguinte
            rt = root_plan(toks)
            if rt:
                add(sid, rt["kind"], rt["conf"], rt["proposal"], text[:120])
        for pos, (_, c) in enumerate(toks):
            if c[3] == "_" and c[1] not in ("_",):
                dist = tab.get(c[1].lower())  # "token N" = N-ésimo token da frase
                if dist:
                    up, k = dist.most_common(1)[0]
                    tot = sum(dist.values())
                    if tot >= 3 and k / tot >= 0.9:
                        add(sid, "fill_upos", "alta" if k / tot >= 0.97 and tot >= 5 else "média",
                            f"token {pos + 1} {c[1]}: UPOS _ → {up}", f"{k}/{tot} ocorrências como {up}")
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    # o que fica para revisão manual
    proposed = {(r["sent_id"]) for r in rows}
    man = []
    if ISSUES.exists():
        with ISSUES.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["severity"] != "error":
                    continue
                if r["category"] in ("token_ids_not_sequential",) and r["sent_id"] in proposed:
                    continue
                if r["category"] == "root_mismatch" and r["sent_id"] in proposed:
                    continue
                man.append(r)
    with MANUAL.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["line", "sent_id", "severity", "category", "detail"], delimiter="\t")
        w.writeheader()
        w.writerows(man)
    c = collections.Counter((r["kind"], r["confidence"]) for r in rows)
    for k, v in sorted(c.items()):
        print(f"{v:5d}  {k[0]:13s} {k[1]}")
    print(f"{len(rows)} propostas em {OUT.relative_to(ROOT)}; {len(man)} erros listados em {MANUAL.relative_to(ROOT)}")


def apply(alta):
    with OUT.open(encoding="utf-8") as fh:
        props = [r for r in csv.DictReader(fh, delimiter="\t")
                 if r["approve"].strip().lower() in ("sim", "s", "yes", "x") or (alta and r["confidence"] == "alta")]
    by_sid = collections.defaultdict(list)
    for r in props:
        by_sid[r["sent_id"]].append(r)
    blocks = read_blocks()
    log, done = [], collections.Counter()
    for b in blocks:
        sid, lines = b
        if sid not in by_sid:
            continue
        toks = toks_of(lines)
        for r in by_sid[sid]:
            k = r["kind"]
            if k == "renumber_ids":
                rp = renumber_plan(toks)
                if not rp:
                    continue
                for pos, (i, c) in enumerate(toks):
                    c = list(c)
                    c[0] = str(pos + 1)
                    c[6] = rp["newheads"][pos]
                    if c[6] == "_" and toks[pos][1][6] not in ("_",):
                        c[7] = "_"
                    lines[i] = "\t".join(c)
            elif k in ("set_root", "reroot"):
                rt = root_plan(toks)
                if not rt or rt["kind"] != k:
                    continue
                i, c = toks[rt["root"]]
                c = list(c)
                if k == "set_root":
                    c[7] = "root"
                    lines[i] = "\t".join(c)
                else:
                    j, v = toks[rt["verb"]]
                    v = list(v)
                    c[6], c[7] = v[0], OLD_TO_NEW_DEPREL.get(c[3], c[7])
                    v[6], v[7] = "0", "root"
                    lines[i], lines[j] = "\t".join(c), "\t".join(v)
            elif k == "fill_upos":
                m = re.match(r"token (\d+) (.+): UPOS _ → (\S+)$", r["proposal"])
                for pos, (i, c) in enumerate(toks):
                    if m and pos + 1 == int(m.group(1)) and c[1] == m.group(2) and c[3] == "_":
                        c = list(c)
                        c[3] = m.group(3)
                        c[9] = add_misc(c[9], "Auto=upos")
                        lines[i] = "\t".join(c)
            toks = toks_of(lines)
            done[k] += 1
            log.append([r["prop_id"], sid, k, r["confidence"], r["proposal"]])
    CONLLU.write_text("\n\n".join("\n".join(l) for _, l in blocks) + "\n\n", encoding="utf-8")
    from datetime import date
    lp = ROOT / f"CorBo/validation/tree_applied_{date.today():%Y%m%d}.tsv"
    with lp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["prop_id", "sent_id", "kind", "confidence", "proposal"])
        w.writerows(log)
    print(dict(done), "→", lp.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--alta", action="store_true", help="com --apply: aplica também as de confiança alta")
    a = ap.parse_args()
    apply(a.alta) if a.apply else propose()
