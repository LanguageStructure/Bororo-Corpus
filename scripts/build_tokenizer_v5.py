#!/usr/bin/env python3
"""Constrói o inventário único do tokenizador para o site (tokenizer-v5-site.json).

Parte do inventário v4 publicado (tokenizer-v4-site.json) e acrescenta, sem
alterar nenhuma análise linguística:

  * pré-tokenização: chaves com espaços, pontuação nas bordas, números e
    pontuação isolada deixam de ser "formas lexicais" (ficam em `non_lexical`);
  * marcação de forma provavelmente portuguesa (`lang_suspect: "pt"`) com a
    evidência gráfica usada — é uma suspeita a revisar, não uma decisão;
  * caracteres da Área de Uso Privado (restos de fontes legadas) excluídos e
    listados em `private_use_forms`;
  * para cada análise: `surface_segments` (fatias da grafia, quando a análise é
    concatenativa) e `underlying_morphemes` (representação morfológica);
    `segments` é mantido para compatibilidade;
  * `review_status` por forma: confirmed | proposed | proposed_low_support |
    unanalysed, substituindo o rótulo "segmented" do v4, que valia para tudo;
  * `support` (nº de ocorrências da família lexical que sustenta a proposta,
    vindo do v2) e `low_support` quando support < LOW_SUPPORT.

Uso:  python3 scripts/build_tokenizer_v5.py
"""
import collections
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data"
V4_SITE = DATA / "tokenizer-v4-site.json"
V2 = DATA / "tokenizer-v2.json"
LEXICON = DATA / "tokenizer-lexicon-v3.json"
OUT = DATA / "tokenizer-v5-site.json"
REPORT = ROOT / "CorBo/validation/tokenizer_v5_report.json"
LOW_SUPPORT = 3

EDGE_PUNCT = "()[]{}\"'“”‘’«».,;:!?…"
# Indícios gráficos de português (o Bororo do corpus é escrito sem diacríticos
# nem estes dígrafos). Suspeita, não classificação.
PT_CHARS = set("ãõáéíóúâêôàçü")
PT_PATTERNS = [(re.compile(r"(lh|nh|qu|ss|rr)"), "dígrafo"), (re.compile(r"(ção|ções|mente)$"), "sufixo")]


def is_pua(ch):
    return 0xE000 <= ord(ch) <= 0xF8FF


def classify_key(key):
    k = unicodedata.normalize("NFC", key).strip()
    if any(is_pua(c) for c in k):
        return "private_use", k
    if not k or not any(c.isalpha() for c in k):
        return "number" if any(c.isdigit() for c in k) else "punctuation", k
    stripped = k.strip(EDGE_PUNCT)
    if " " in stripped:
        return "multiword", k
    if stripped.startswith("-") or stripped.endswith("-"):
        return "affix_citation", stripped
    return "word", stripped


def pt_evidence(form):
    ev = sorted({c for c in form if c in PT_CHARS})
    if ev:
        return "diacrítico " + "".join(ev)
    for rx, label in PT_PATTERNS:
        m = rx.search(form)
        if m:
            return f"{label} '{m.group(1)}'"
    return None


def main():
    v4 = json.loads(V4_SITE.read_text(encoding="utf-8"))
    forms4 = v4["forms"]
    v2 = json.loads(V2.read_text(encoding="utf-8")).get("analyses", {})
    lexicon = json.loads(LEXICON.read_text(encoding="utf-8")).get("entries", {}) if LEXICON.exists() else {}

    forms, non_lexical, pua, merged = {}, collections.Counter(), [], collections.Counter()
    for key, entry in forms4.items():
        kind, clean = classify_key(key)
        if kind == "private_use":
            pua.append(key)
            continue
        if kind in ("number", "punctuation", "multiword", "affix_citation"):
            non_lexical[kind] += entry.get("frequency", 0) or 1
            continue
        clean = clean.lower()
        e = json.loads(json.dumps(entry))  # cópia
        if clean != key:
            merged[clean] += 1
            if clean in forms:  # a forma limpa já existe: só soma a frequência
                forms[clean]["frequency"] = forms[clean].get("frequency", 0) + e.get("frequency", 0)
                continue
            if clean in forms4:
                continue  # a entrada limpa será processada por si mesma
        support = (v2.get(clean) or {}).get("support")
        analyses = []
        for a in e.get("analyses", []):
            segs = a.get("segments") or []
            concat = "".join(segs).lower() == clean
            lex = lexicon.get(clean)
            a = dict(a)
            a["concatenative"] = concat
            a["underlying_morphemes"] = (lex or {}).get("underlying_morphemes") or segs
            lex_surface = (lex or {}).get("surface_segments")
            if concat:
                a["surface_segments"] = segs
            elif lex_surface and "".join(lex_surface).lower() == clean:
                a["surface_segments"] = lex_surface
            else:
                a["surface_segments"] = None  # só a representação subjacente é conhecida
            if a.get("status") == "proposed" and support is not None:
                a["support"] = support
                a["low_support"] = support < LOW_SUPPORT
            analyses.append(a)
        e["analyses"] = analyses
        status = e.get("status", "unanalysed")
        if status == "proposed" and support is not None and support < LOW_SUPPORT:
            status = "proposed_low_support"
        e["review_status"] = status
        if support is not None:
            e["support"] = support
        ev = pt_evidence(clean)
        if ev:
            e["lang_suspect"] = "pt"
            e["lang_evidence"] = ev
        forms[clean] = e

    counts = collections.Counter(e["review_status"] for e in forms.values())
    out = {
        "schema": "corbo-tokenizer-v5-site/v1",
        "generated": date.today().isoformat(),
        "derived_from": ["docs/data/tokenizer-v4-site.json", "docs/data/tokenizer-v2.json (support)",
                         "docs/data/tokenizer-lexicon-v3.json (surface/underlying)"],
        "policy": "Reconhecimento não equivale a segmentação verificada. 'proposed' não é verificado; "
                  "'proposed_low_support' tem família lexical com menos de %d ocorrências. "
                  "lang_suspect é uma suspeita gráfica, não uma classificação." % LOW_SUPPORT,
        "review_status_counts": dict(counts),
        "lang_suspect_pt": sum(1 for e in forms.values() if e.get("lang_suspect") == "pt"),
        "non_lexical_tokens": dict(non_lexical),
        "private_use_forms": pua,
        "forms": dict(sorted(forms.items())),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    report = {k: v for k, v in out.items() if k != "forms"}
    report["pt_suspects"] = sorted((k, e["lang_evidence"]) for k, e in forms.items() if e.get("lang_suspect"))
    report["non_concatenative_confirmed"] = sorted(
        k for k, e in forms.items() for a in e["analyses"] if a.get("status") == "confirmed" and not a["concatenative"])
    report["edge_punctuation_merged"] = dict(merged)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(forms)} formas lexicais · {dict(counts)} · pt suspeitas: {out['lang_suspect_pt']} · "
          f"não lexicais: {dict(non_lexical)} · PUA: {len(pua)}")


if __name__ == "__main__":
    main()
