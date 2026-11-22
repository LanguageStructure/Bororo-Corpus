#!/usr/bin/env python3
"""Validação estrutural e de rótulos do CoNLL-U do CorBo (sem dependências externas).

Complementa (não substitui) o validador oficial do UD (tools/validate.py).
Cada problema é registrado com número de linha, sent_id, categoria e severidade.

Uso:
  python3 scripts/validate_conllu.py CorBo/Corpus_Files/CorBo.conllu \
      --report CorBo/validation/issues.tsv --summary CorBo/validation/summary.json
  # Modo CI: falha se alguma categoria de erro piorar em relação à linha de base
  python3 scripts/validate_conllu.py CorBo/Corpus_Files/CorBo.conllu \
      --baseline CorBo/validation/baseline.json
"""
import argparse
import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "CorBo/validation/feature_inventory.json"

UD_UPOS = set("ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X".split())
UD_DEPREL = set(
    "acl advcl advmod amod appos aux case cc ccomp clf compound conj cop csubj dep det discourse "
    "dislocated expl fixed flat goeswith iobj list mark nmod nsubj nummod obj obl orphan parataxis "
    "punct reparandum root vocative xcomp".split()
)
PUNCT_RE = re.compile(r"[\s\"'“”‘’«»()\[\]{}.,;:!?…\-–—/]+")


def is_pua(ch):
    o = ord(ch)
    return 0xE000 <= o <= 0xF8FF or 0xF0000 <= o <= 0x10FFFD


def read_blocks(path):
    """Devolve blocos (linha_inicial, [(nº_linha, texto)]) separados por linha em branco."""
    blocks, cur = [], []
    with open(path, encoding="utf-8") as fh:
        for n, raw in enumerate(fh, 1):
            line = raw.rstrip("\n").rstrip("\r")
            if line.strip() == "":
                if cur:
                    blocks.append(cur)
                    cur = []
                continue
            cur.append((n, line))
    if cur:
        blocks.append(cur)
    return blocks


def load_inventory():
    if INVENTORY.exists():
        data = json.loads(INVENTORY.read_text(encoding="utf-8"))
        return {k: set(v["values"]) for k, v in data["features"].items()}
    return None


def validate(path):
    inventory = load_inventory()
    issues = []
    stats = collections.Counter()
    seen_ids = {}

    def add(line, sid, cat, sev, detail):
        issues.append({"line": line, "sent_id": sid or "", "category": cat, "severity": sev, "detail": detail})

    for block in read_blocks(path):
        comments = [(n, l) for n, l in block if l.startswith("#")]
        tokens = [(n, l) for n, l in block if not l.startswith("#")]
        meta = {}
        for n, l in comments:
            m = re.match(r"#\s*([^=]+?)\s*=\s*(.*)$", l)
            if m and m.group(1) not in meta:
                meta[m.group(1)] = (n, m.group(2))
        first = block[0][0]
        sid = meta.get("sent_id", (None, None))[1]
        stats["blocks"] += 1
        if not tokens:
            if sid is not None:
                stats["sentences_pending_tokenization"] += 1
                add(first, sid, "pending_tokenization", "warning", "unidade sem tokens (texto ainda não tokenizado/anotado)")
            else:
                add(first, sid, "block_without_tokens", "error", "bloco só com comentários, sem sent_id")
            continue
        stats["sentences"] += 1
        if sid is None:
            if "sent_id_original" in meta:
                add(first, None, "missing_sent_id", "error", "tem sent_id_original mas não sent_id")
            else:
                add(first, None, "fragment_without_sent_id", "error",
                    "bloco sem comentários separado por linha em branco (provável continuação da sentença anterior)")
        else:
            if sid in seen_ids:
                add(first, sid, "duplicate_sent_id", "error", f"também na linha {seen_ids[sid]}")
            seen_ids[sid] = first
        if "text" not in meta and sid is not None:
            add(first, sid, "missing_text", "error", "sem # text")
        auto = any(k == "auto_annotation" for k in meta)
        stats["auto_sentences" if auto else "manual_sentences"] += 1

        words, heads, forms = [], {}, []
        partial = False
        for n, l in tokens:
            f = l.split("\t")
            if len(f) != 10:
                add(n, sid, "wrong_column_count", "error", f"{len(f)} colunas")
                continue
            tid, form, lemma, upos, xpos, feats, head, deprel, deps, misc = f
            if re.fullmatch(r"\d+-\d+", tid):
                continue
            if re.fullmatch(r"\d+\.\d+", tid):
                continue
            if not re.fullmatch(r"[1-9]\d*", tid):
                add(n, sid, "bad_token_id", "error", tid)
                continue
            stats["tokens"] += 1
            words.append(tid)
            forms.append(form)
            if "Auto=" in misc:
                stats["auto_tokens"] += 1
            for col, val in (("FORM", form), ("LEMMA", lemma)):
                if val != val.strip():
                    add(n, sid, "whitespace_in_" + col.lower(), "error", repr(val))
                if any(is_pua(c) for c in val):
                    add(n, sid, "private_use_character", "error", f"{col}={val!r}")
                if unicodedata.normalize("NFC", val) != val:
                    add(n, sid, "not_nfc", "error", f"{col}={val!r}")
            if upos not in UD_UPOS:
                add(n, sid, "upos_missing" if upos == "_" else "upos_not_ud", "error", repr(upos))
            if feats != "_":
                items = feats.split("|")
                keys = []
                for kv in items:
                    if "=" not in kv:
                        add(n, sid, "feat_malformed", "error", repr(kv))
                        continue
                    k, v = kv.split("=", 1)
                    keys.append(k)
                    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*(\[[a-z0-9]+\])?", k) or not re.fullmatch(r"[A-Z0-9][A-Za-z0-9]*(,[A-Z0-9][A-Za-z0-9]*)*", v):
                        add(n, sid, "feat_malformed", "error", repr(kv))
                    elif inventory is not None and (k not in inventory or v not in inventory[k]):
                        add(n, sid, "feat_undocumented", "warning", kv)
                if items != sorted(items, key=lambda x: x.split("=")[0].lower()):
                    add(n, sid, "feats_unsorted", "error", feats)
                if len(keys) != len(set(keys)):
                    add(n, sid, "feat_duplicate_key", "error", feats)
            if misc != "_":
                for item in misc.split("|"):
                    if item == "_" or "=" not in item:
                        add(n, sid, "misc_malformed", "warning", repr(item))
            if head == "_" or deprel == "_":
                partial = True
                if head != deprel and "_" in (head, deprel):
                    add(n, sid, "head_deprel_mismatch", "warning", f"HEAD={head} DEPREL={deprel}")
            else:
                if not re.fullmatch(r"\d+", head):
                    add(n, sid, "bad_head", "error", head)
                    partial = True
                else:
                    heads[tid] = (head, n)
                if deprel.split(":")[0] not in UD_DEPREL:
                    add(n, sid, "deprel_not_ud", "error", deprel)
                if (head == "0") != (deprel == "root"):
                    add(n, sid, "root_mismatch", "error", f"HEAD={head} DEPREL={deprel}")

        if words != [str(i) for i in range(1, len(words) + 1)]:
            add(first, sid, "token_ids_not_sequential", "error", " ".join(words[:12]) + (" …" if len(words) > 12 else ""))
        if "text" in meta:
            text = meta["text"][1]
            a, b = re.sub(r"\s", "", text), "".join(forms)
            if a != b:
                if PUNCT_RE.sub("", text) == PUNCT_RE.sub("", " ".join(forms)):
                    add(meta["text"][0], sid, "text_punct_mismatch", "warning", "difere só em pontuação/aspas")
                else:
                    add(meta["text"][0], sid, "text_form_mismatch", "error", f"text={text[:60]!r} | forms={' '.join(forms)[:60]!r}")
        if partial or not heads:
            stats["sentences_without_full_syntax"] += 1
            continue
        stats["sentences_with_full_syntax"] += 1
        roots = [t for t, (h, _) in heads.items() if h == "0"]
        if len(roots) != 1:
            add(first, sid, "root_count", "error", f"{len(roots)} raízes")
        for t, (h, n) in heads.items():
            if h != "0" and h not in heads:
                add(n, sid, "head_out_of_range", "error", f"{t}→{h}")
        for start in heads:
            seen, x = set(), start
            while x in heads and heads[x][0] != "0":
                if x in seen:
                    add(first, sid, "cycle", "error", "ciclo envolvendo o token " + x)
                    break
                seen.add(x)
                x = heads[x][0]
            else:
                continue
            break

    return issues, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("conllu")
    ap.add_argument("--report", help="TSV com todos os problemas")
    ap.add_argument("--summary", help="JSON com contagens")
    ap.add_argument("--baseline", help="JSON de linha de base; falha se alguma categoria de erro aumentar")
    ap.add_argument("--strict", action="store_true", help="falha com qualquer erro")
    args = ap.parse_args()

    issues, stats = validate(args.conllu)
    by_cat = collections.Counter((i["severity"], i["category"]) for i in issues)
    errors = {c: n for (s, c), n in by_cat.items() if s == "error"}
    warnings = {c: n for (s, c), n in by_cat.items() if s == "warning"}
    summary = {"file": args.conllu, "stats": dict(stats), "errors": dict(sorted(errors.items())),
               "warnings": dict(sorted(warnings.items())), "error_total": sum(errors.values())}

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, ["line", "sent_id", "severity", "category", "detail"], delimiter="\t")
            w.writeheader()
            for i in sorted(issues, key=lambda x: (x["severity"] != "error", x["category"], x["line"])):
                w.writerow(i)
    if args.summary:
        Path(args.summary).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    status = 0
    if args.baseline:
        base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))["errors"]
        worse = {c: (base.get(c, 0), n) for c, n in errors.items() if n > base.get(c, 0)}
        if worse:
            print("\nERRO: categorias que pioraram em relação à linha de base:", file=sys.stderr)
            for c, (b, n) in sorted(worse.items()):
                print(f"  {c}: {b} → {n}", file=sys.stderr)
            status = 1
        else:
            print("\nNenhuma categoria de erro piorou em relação à linha de base.")
    if args.strict and errors:
        status = 1
    sys.exit(status)


if __name__ == "__main__":
    main()
