#!/usr/bin/env python3
"""Constrói o inventário v6 do tokenizador (docs/data/tokenizer-v6-site.json) a partir do v5.

Mudanças em relação ao v5 (nenhuma decide análise nova; só aplica análises já feitas por FFG ou decisões
registradas em planilha):

1. **Morph= do CoNLL-U como fonte de verdade.** Toda forma que tem `Morph=` em tokens anotados à mão
   (sem `morph` em `Auto=`) e uma única análise passa a `confirmed`, com:
     - `morph`: a análise como no CoNLL-U (`e=ako=re`, `0-ji`), com `=` (clítico), `-` (afixo) e `0` (zero);
     - `underlying_morphemes`: os morfemas da análise, sem os expoentes zero;
     - `surface_segments`: as fatias da grafia, quando a análise é concatenativa; senão, a segmentação de
       superfície confirmada no v5, se houver (ex.: *egore* `e+go+re` ↔ `e=ako=re`).
   A análise anterior do v5 fica registrada em `CorBo/validation/tokenizer_v6_morph_<data>.tsv`.
2. **Hipóteses em palavras de classe fechada.** Formas cuja classe majoritária no CoNLL-U é ADP, ADV, PRON,
   DET, SCONJ, CCONJ, PART, INTJ, AUX ou NUM e que têm segmentação não confirmada no v5 vão para
   `CorBo/validation/tokenizer_v6_classe_fechada.tsv` (colunas `sugestao` e `decisao`). Só as linhas com
   `decisao=remover` são aplicadas: a forma fica sem segmentação (`unanalysed`). Decisões já preenchidas
   são preservadas quando a planilha é gerada de novo.

Uso: python3 scripts/build_tokenizer_v6.py            (simula)
     python3 scripts/build_tokenizer_v6.py --apply    (grava o v6, o registro e a planilha)
"""
import argparse
import collections
import csv
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V5 = ROOT / "docs/data/tokenizer-v5-site.json"
OUT = ROOT / "docs/data/tokenizer-v6-site.json"
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
VAL = ROOT / "CorBo/validation"
CLOSED_TSV = VAL / "tokenizer_v6_classe_fechada.tsv"
REPORT = VAL / "tokenizer_v6_report.json"
CLOSED = {"ADP", "ADV", "PRON", "DET", "SCONJ", "CCONJ", "PART", "INTJ", "AUX", "NUM"}
CLOSED_SHARE = 0.8
# Índices pessoais (clíticos): uma hipótese que começa por um deles pode ser uma análise legítima
# (ex.: e=tae), então não é sugerida para remoção.
PERSON = {"i", "a", "u", "e", "pa", "ce", "ta", "tu"}


def nfc(s):
    return unicodedata.normalize("NFC", s)


def read_conllu():
    morph = collections.defaultdict(collections.Counter)      # forma -> análise -> tokens (manuais)
    morph_auto = collections.Counter()
    upos = collections.defaultdict(collections.Counter)
    readings = collections.defaultdict(collections.Counter)     # forma -> (lema, UPOS) -> tokens
    morph_readings = collections.defaultdict(collections.Counter)
    for line in CONLLU.open(encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if len(c) != 10 or not c[0].isdigit():
            continue
        form = nfc(c[1]).casefold()
        if c[3] not in ("_", ""):
            upos[form][c[3]] += 1
        readings[form][(nfc(c[2]).casefold(), c[3])] += 1
        misc = c[9]
        m = re.search(r"(?:^|\|)Morph=([^|]+)", misc)
        if not m:
            continue
        auto = " ".join(v for k, v in re.findall(r"(?:^|\|)(Auto[^=|]*)=([^|]*)", misc))
        if "morph" in auto.casefold():
            morph_auto[form] += 1
            continue
        morph[form][nfc(m.group(1))] += 1
        morph_readings[form][(nfc(c[2]).casefold(), c[3])] += 1
    return morph, morph_auto, upos, readings, morph_readings


def parse_morph(value):
    pieces = [p for p in re.split(r"[-=]", value)]
    seps = re.findall(r"[-=]", value)
    return pieces, seps


def first_analysis(entry):
    for a in (entry or {}).get("analyses", []) or []:
        return a
    return None


def fmt(a):
    if not a:
        return ""
    return "+".join(a.get("surface_segments") or a.get("segments") or [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    v5 = json.loads(V5.read_text(encoding="utf-8"))
    forms = json.loads(json.dumps(v5["forms"]))     # cópia
    morph, morph_auto, upos, readings, morph_readings = read_conllu()
    today = date.today().isoformat()

    # 1. Morph= do CoNLL-U
    log, conflicts, homographs = [], [], []
    for form, counter in sorted(morph.items()):
        if len(counter) > 1:
            conflicts.append({"form": form, "analyses": dict(counter)})
            continue
        value, n = counter.most_common(1)[0]
        # A segmentação vale para a forma inteira: se a maioria dos tokens dessa grafia tem outra leitura
        # (outro lema ou outra classe), a análise de poucos tokens não é generalizada (ex.: homógrafos).
        mr = set(morph_readings[form])
        other = sum(k for r, k in readings[form].items() if r not in mr)
        if other > sum(readings[form][r] for r in mr):
            homographs.append({"form": form, "morph": value, "morph_tokens": n,
                               "readings_with_morph": ["/".join(r) for r in mr],
                               "other_readings": {"/".join(r): k for r, k in readings[form].items() if r not in mr}})
            continue
        pieces, seps = parse_morph(value)
        nonzero = [p for p in pieces if p != "0"]
        old = forms.get(form)
        olda = first_analysis(old)
        surface = None
        if "".join(nonzero) == form:
            surface = nonzero
        else:
            for a in (old or {}).get("analyses", []) or []:
                s = a.get("surface_segments") or a.get("segments") or []
                if s and "".join(s) == form and a.get("status") == "confirmed":
                    surface = s
                    break
        analysis = {
            "segments": surface or nonzero,
            "surface_segments": surface,
            "underlying_morphemes": nonzero,
            "morph": value,
            "boundaries": seps,
            "zero_morphemes": pieces.count("0"),
            "source": "conllu_morph",
            "status": "confirmed",
            "kind": "lexical",
            "concatenative": bool(surface),
            "tokens": n,
        }
        if old is None:
            change = "nova"
            forms[form] = {"category": "conllu_morph", "status": "segmented", "frequency": n}
        elif old.get("review_status") == "confirmed" and olda and (olda.get("surface_segments") or olda.get("segments")) == analysis["segments"]:
            change = "confirmada_igual"
        elif old.get("review_status") == "confirmed":
            change = "confirmada_nova_analise"
        else:
            change = "promovida_de_" + str(old.get("review_status"))
        forms[form]["analyses"] = [analysis]
        forms[form]["review_status"] = "confirmed"
        log.append({"form": form, "morph": value, "surface_segments": "+".join(surface) if surface else "",
                    "tokens": n, "status_v5": (old or {}).get("review_status", "ausente"),
                    "analise_v5": fmt(olda), "fonte_v5": (olda or {}).get("source", ""), "mudanca": change})

    # 2. classe fechada: planilha de decisão (preserva decisões já tomadas)
    prev = {}
    if CLOSED_TSV.exists():
        with CLOSED_TSV.open(encoding="utf-8") as fh:
            prev = {r["form"]: r for r in csv.DictReader(fh, delimiter="\t")}
    closed_rows, removed = [], []
    for form, entry in sorted(forms.items()):
        if form in morph or entry.get("review_status") == "confirmed":
            continue
        a = first_analysis(entry)
        seg = (a or {}).get("segments") or []
        if len(seg) < 2:
            continue
        u = upos.get(form)
        if not u:
            continue
        top, k = u.most_common(1)[0]
        if top not in CLOSED or k / sum(u.values()) < CLOSED_SHARE:
            continue
        if seg[0] in PERSON:
            sug = "revisar: índice pessoal + base"
        elif seg[-1] == "re":
            sug = "revisar: base + =re"
        elif a.get("kind") == "hypothesis" or a.get("source") == "productive_attested_stem":
            sug = "remover"
        else:
            sug = "revisar"
        decisao = (prev.get(form, {}).get("decisao") or "").strip()
        closed_rows.append({"form": form, "upos": " ".join(f"{p}:{c}" for p, c in u.most_common()),
                            "tokens_conllu": sum(u.values()), "status_v5": entry.get("review_status"),
                            "analise_v5": "+".join(seg), "fonte_v5": a.get("source", ""), "sugestao": sug,
                            "decisao": decisao})
        if decisao.casefold() == "remover":
            entry["analyses"] = []
            entry["review_status"] = "unanalysed"
            entry["note"] = f"segmentação removida em {today}: palavra de classe fechada ({top}); ver {CLOSED_TSV.name}"
            removed.append(form)

    counts = collections.Counter(e.get("review_status") for e in forms.values())
    out = {k: v for k, v in v5.items() if k != "forms"}
    out.update({
        "schema": "corbo-tokenizer-v6-site/v1",
        "generated": today,
        "derived_from": ["docs/data/tokenizer-v5-site.json", "CorBo/Corpus_Files/CorBo.conllu (MISC Morph=)"],
        "policy": v5.get("policy", "") + " Análises com 'morph' vêm do Morph= do CoNLL-U, anotado à mão "
                  "('=' clítico, '-' afixo, '0' expoente zero).",
        "review_status_counts": dict(sorted(counts.items())),
        "conllu_morph_forms": len(log),
        "forms": forms,
    })
    report = {
        "generated": today,
        "conllu_morph": {"forms_applied": len(log), "changes": dict(collections.Counter(r["mudanca"] for r in log)),
                         "conflicting_forms": conflicts, "homographs_not_generalized": homographs,
                         "tokens_with_auto_morph_ignored": sum(morph_auto.values())},
        "closed_class": {"rows": len(closed_rows), "suggestions": dict(collections.Counter(r["sugestao"] for r in closed_rows)),
                         "decided_remove": len(removed)},
        "review_status_counts_v5": v5.get("review_status_counts"),
        "review_status_counts_v6": dict(sorted(counts.items())),
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if not args.apply:
        print("Simulação: nada foi gravado (use --apply).")
        return
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    logp = VAL / f"tokenizer_v6_morph_{today.replace('-', '')}.tsv"
    for path, rows in ((logp, log), (CLOSED_TSV, closed_rows)):
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, list(rows[0]) if rows else ["form"], delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    print("Gravado:", OUT.relative_to(ROOT), REPORT.relative_to(ROOT), logp.relative_to(ROOT), CLOSED_TSV.relative_to(ROOT))


if __name__ == "__main__":
    main()
