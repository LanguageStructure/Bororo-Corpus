#!/usr/bin/env python3
"""Gera o índice lexical compacto usado pelo painel lateral do site.

Para cada forma gráfica (minúsculas, NFC) reúne, já calculado:
  freq          ocorrências nos textos documentais publicados (corbo-units.json)
  collections   coleções onde a forma ocorre (até 6)
  conllu        ocorrências no CoNLL-U, lemas, classes, traços, segmentações
                (Morph=), relações, glosas e um sent_id para a árvore UD
  tokenizer     estado de revisão e segmentação do inventário v5
  dict          entradas do dicionário público (pela forma ou pelos lemas)
  examples      até 2 unidades documentais com tradução

A saída é dividida por letra inicial em docs/data/lexicon/<letra>.json, para o
painel baixar só o necessário. Derivado; reconstruído pelo build.
"""
import collections
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data"
OUT = DATA / "lexicon"
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?")


def norm(s):
    return unicodedata.normalize("NFC", str(s or "")).casefold().strip()


def shard(form):
    c = unicodedata.normalize("NFD", form)[:1]
    return c if "a" <= c <= "z" else "_"


def top(counter, n=4):
    return [[k, v] for k, v in counter.most_common(n) if k and k != "_"]


def main():
    lex = collections.defaultdict(lambda: {"freq": 0, "coll": collections.Counter(), "ex": []})

    units = json.loads((DATA / "corbo-units.json").read_text(encoding="utf-8"))
    for u in units:
        text, trans = u.get("b") or "", u.get("p") or ""
        seen = set()
        for w in WORD.findall(text):
            f = norm(w)
            e = lex[f]
            e["freq"] += 1
            if f in seen:
                continue
            seen.add(f)
            e["coll"][u.get("collection") or ""] += 1
            if len(e["ex"]) < 2 and trans.strip() and len(text) < 400:
                e["ex"].append({"id": u.get("id", ""), "c": u.get("collection", ""),
                                "b": text.strip()[:220], "p": trans.strip()[:220]})

    conll = collections.defaultdict(lambda: {"n": 0, "lemma": collections.Counter(), "upos": collections.Counter(),
                                             "feats": collections.Counter(), "morph": collections.Counter(),
                                             "deprel": collections.Counter(), "gloss": collections.Counter(), "sid": ""})
    sid = ""
    for line in CONLLU.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"#\s*sent_id\s*=\s*(.*)$", line)
        if m:
            sid = m.group(1).strip()
            continue
        f = line.split("\t")
        if len(f) != 10 or not f[0].isdigit():
            continue
        c = conll[norm(f[1])]
        c["n"] += 1
        c["lemma"][f[2]] += 1
        c["upos"][f[3]] += 1
        c["feats"][f[5]] += 1
        c["deprel"][f[7]] += 1
        misc = dict(x.split("=", 1) for x in f[9].split("|") if "=" in x)
        if misc.get("Morph") or misc.get("MORPH"):
            c["morph"][misc.get("Morph") or misc.get("MORPH")] += 1
        if misc.get("Gloss"):
            c["gloss"][misc["Gloss"].replace("_", " ")] += 1
        if not c["sid"] and sid and f[6] not in ("_", ""):
            c["sid"] = sid

    tok = json.loads((DATA / "tokenizer-v5-site.json").read_text(encoding="utf-8"))["forms"] \
        if (DATA / "tokenizer-v5-site.json").exists() else {}
    dic = json.loads((DATA / "dicionario-bororo-publico.json").read_text(encoding="utf-8")).get("entries", [])
    by_key = collections.defaultdict(list)
    for d in dic:
        item = {k: d.get(k, "") for k in ("entry", "ipa", "pos", "definition", "example_sent", "comment") if d.get(k)}
        for k in {norm(d.get("entry")), norm(d.get("lemma_key"))} - {""}:
            if len(by_key[k]) < 4:
                by_key[k].append(item)

    forms = set(lex) | set(conll)
    shards = collections.defaultdict(dict)
    for f in forms:
        if not f or not any(ch.isalpha() for ch in f):
            continue
        rec = {}
        e = lex.get(f)
        if e and e["freq"]:
            rec["freq"] = e["freq"]
            rec["coll"] = top(e["coll"], 6)
            if e["ex"]:
                rec["ex"] = e["ex"]
        c = conll.get(f)
        lemmas = []
        if c and c["n"]:
            lemmas = [k for k, _ in c["lemma"].most_common(3) if k != "_"]
            rec["ud"] = {"n": c["n"], "lemma": top(c["lemma"], 3), "upos": top(c["upos"], 3),
                         "feats": top(c["feats"], 3), "morph": top(c["morph"], 3),
                         "deprel": top(c["deprel"], 3), "gloss": top(c["gloss"], 3), "sid": c["sid"]}
        t = tok.get(f)
        if t:
            a = next((x for x in t.get("analyses", []) if len(x.get("segments") or []) > 1), None)
            rec["tok"] = {"st": t.get("review_status", t.get("status", "unanalysed"))}
            if a:
                rec["tok"].update({"seg": a.get("segments"), "under": a.get("underlying_morphemes"),
                                   "concat": a.get("concatenative", True)})
                if a.get("low_support"):
                    rec["tok"]["support"] = a.get("support")
            if t.get("lang_suspect"):
                rec["tok"]["pt"] = t.get("lang_evidence", "")
        entries = []
        for k in [f] + [norm(x) for x in lemmas]:
            for item in by_key.get(k, []):
                if item not in entries:
                    entries.append(item)
        if entries:
            rec["dict"] = entries[:4]
        if rec:
            shards[shard(f)][f] = rec

    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for key, data in shards.items():
        (OUT / f"{key}.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        total += len(data)
    (OUT / "index.json").write_text(json.dumps({"schema": "corbo-lexicon-panel/v1", "shards": sorted(shards),
                                                "forms": total}, ensure_ascii=False), encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.glob("*.json"))
    print(f"{total} formas em {len(shards)} partes, {size/1e6:.1f} MB no total")


if __name__ == "__main__":
    main()
