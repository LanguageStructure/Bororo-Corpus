#!/usr/bin/env python3
"""Gera docs/data/interlinear.json: glosa interlinear das unidades dos leitores que
correspondem a uma sentença anotada do CoNLL-U.

Correspondência: o texto Bororo da unidade (corbo-units.json) e o # text da
sentença são comparados sem caixa, espaços e pontuação.

Para cada token gravam-se três linhas:
  forma     FORM
  segm      segmentação de Morph= (ex.: e=ako=re); vazio se não houver
  glosa     glosa automática:
              - radical: Gloss= do MISC, senão a definição do dicionário público
                quando o lema tem uma única entrada (abreviada, com pontos), senão
                o próprio lema;
              - morfemas antes do radical: pessoa e número dos traços (0 = 3);
              - =re com Mood=Ind: IND; outros morfemas sem glosa ficam como estão;
              - sem Morph=: radical + abreviaturas dos traços flexionais.
A glosa é derivada da anotação e não substitui uma glosa revisada.

  python3 scripts/build_interlinear.py
"""
import collections
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data"
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUT = DATA / "interlinear.json"

PN = {"Sing": "SG", "Plur": "PL"}
TAGS = [  # (traço, valor) → abreviatura, na ordem em que aparecem na glosa
    ("Voice", "Cau", "CAUS"), ("Voice", "Pass", "PASS"), ("Voice", "CauPass", "CAUS.PASS"),
    ("Voice", "CauInc", "CAUS.INCH"), ("Aspect", "Prog", "PROG"), ("Aspect", "Inc", "INCH"),
    ("Aspect", "IncProg", "INCH.PROG"), ("Mood", "Ind", "IND"), ("Mood", "Sub", "SBJV"),
    ("Mood", "Imp", "IMP"), ("Mood", "Opt", "OPT"), ("Mood", "Quot", "QUOT"),
    ("Polarity", "Neg", "NEG"), ("Status", "Irr", "IRR"), ("Number", "Plur", "PL"),
    ("Number", "Sgtv", "SGTV"), ("Degree", "Dim", "DIM"), ("Degree", "Aug", "AUG"),
    ("Nomzr", "Rel", "NMLZ"), ("Nomzr", "Loc", "NMLZ.LOC"), ("Reflex", "Yes", "REFL"),
    ("Emph", "Yes", "EMPH"), ("VerbForm", "Ger", "GER"),
]
INFLECTING = {"VERB", "AUX"}


def key(s):
    s = unicodedata.normalize("NFC", s or "").casefold()
    return re.sub(r"[\W_]+", "", s)


def feats_of(s):
    return {} if s in ("_", "") else dict(f.split("=", 1) for f in s.split("|") if "=" in f)


def misc_of(s):
    return {} if s in ("_", "") else dict(f.split("=", 1) for f in s.split("|") if "=" in f)


def short_def(text):
    t = re.split(r"[;,(=]| ou ", text or "")[0].strip().rstrip(".")
    words = t.split()
    if not words or len(words) > 4:
        return None
    return ".".join(words)


def load_dictionary():
    try:
        entries = json.loads((DATA / "dicionario-bororo-publico.json").read_text(encoding="utf-8"))["entries"]
    except (OSError, KeyError, ValueError):
        return {}
    by = collections.defaultdict(list)
    for e in entries:
        by[key(re.sub(r"\d+$", "", e.get("entry", "")))].append(e)
    out = {}
    for k, es in by.items():
        if len(es) == 1:  # homógrafos ficam sem glosa: não há como escolher a acepção
            g = short_def(es[0].get("definition", ""))
            if g:
                out[k] = g
    return out


def person(f):
    p = f.get("Person")
    if not p:
        return None
    lab = p + PN.get(f.get("Number", ""), "")
    if f.get("Clusivity") == "Ex":
        lab += ".EXCL"
    elif f.get("Clusivity") == "In":
        lab += ".INCL"
    return lab


def gloss_token(c, dic):
    form, lemma, upos, feats, misc = c[1], c[2], c[3], feats_of(c[5]), misc_of(c[9])
    if upos == "PUNCT":
        return form, "", ""
    stem_gloss = (misc.get("Gloss") or "").replace("_", ".").replace(",", "/") or dic.get(key(lemma)) or lemma.lower()
    if upos == "PROPN":
        stem_gloss = lemma
    seg = misc.get("Morph") or misc.get("MORPH") or ""
    if seg:
        parts = re.split(r"([-=])", seg)
        morphs = parts[0::2]
        seps = parts[1::2]
        lk = key(lemma)
        si = next((i for i, m in enumerate(morphs) if key(m) == lk), None)
        if si is None:
            si = max(range(len(morphs)), key=lambda i: len(morphs[i]))
        glossed = []
        for i, m in enumerate(morphs):
            if i == si:
                g = stem_gloss
            elif i < si:
                g = "3" if m == "0" else (person(feats) or m)
            elif m == "re" and feats.get("Mood") == "Ind":
                g = "IND"
            else:
                g = m
            glossed.append(g)
        gl = glossed[0] + "".join(s + g for s, g in zip(seps, glossed[1:]))
        return form, seg, gl
    tags = []
    if upos in INFLECTING or upos == "PRON":
        p = person(feats)
        if p and upos == "PRON":
            tags.append(p)
    for feat, val, ab in TAGS:
        if feats.get(feat) == val and (upos in INFLECTING or feat in ("Number", "Degree", "Nomzr", "Reflex", "Emph")):
            if feat == "Number" and (upos == "PRON" or (upos in INFLECTING and person(feats))):
                continue  # o número já está na etiqueta de pessoa (3PL)
            tags.append(ab)
    if upos in INFLECTING and person(feats) and not seg:
        tags.insert(0, person(feats))
    return form, "", ".".join([stem_gloss] + tags)


def main():
    dic = load_dictionary()
    sents = {}
    for block in CONLLU.read_text(encoding="utf-8").split("\n\n"):
        lines = block.strip("\n").split("\n")
        text = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("# text =")), None)
        sid = next((l.split("=", 1)[1].strip() for l in lines if l.startswith("# sent_id")), None)
        toks = [l.split("\t") for l in lines if l and l[0].isdigit() and len(l.split("\t")) == 10]
        toks = [c for c in toks if c[0].isdigit()]
        if text and sid and toks:
            sents.setdefault(key(text), (sid, toks))
    units = json.loads((DATA / "corbo-units.json").read_text(encoding="utf-8"))
    out, per = {}, collections.Counter()
    for u in units:
        hit = sents.get(key(u.get("b")))
        if not hit:
            continue
        sid, toks = hit
        out[u["id"]] = {"sid": sid, "c": u.get("collection", ""), "p": (u.get("p") or "").strip(),
                        "t": [list(gloss_token(c, dic)) for c in toks]}
        per[u.get("collection", "")] += 1
    payload = {
        "note": "Glosa gerada automaticamente da anotação do CoNLL-U (lema, traços, Morph=) e do dicionário público; não substitui uma glosa revisada.",
        "units": out,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(out)} unidades com glosa interlinear → {OUT.relative_to(ROOT)}", dict(per.most_common()))


if __name__ == "__main__":
    main()
