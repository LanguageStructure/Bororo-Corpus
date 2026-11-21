#!/usr/bin/env python3
"""Gera o inventário de rótulos do CorBo a partir do CoNLL-U canônico.

Saídas:
  CorBo/validation/feature_inventory.json  — usado por validate_conllu.py
  docs/ANNOTATION_INVENTORY.md              — tabelas para o guia de anotação

Um valor entra no inventário se tiver descrição registrada abaixo (DESCRIPTIONS)
ou ocorrer pelo menos MIN_COUNT vezes. Valores raros e sem descrição ficam de
fora e aparecem como `feat_undocumented` no validador, para revisão.
As descrições marcadas "(a confirmar)" são rascunhos e precisam de revisão do anotador.
"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUT_JSON = ROOT / "CorBo/validation/feature_inventory.json"
OUT_MD = ROOT / "docs/ANNOTATION_INVENTORY.md"
MIN_COUNT = 3

# (descrição, origem): "UD" = valor universal; "CorBo" = extensão específica do Bororo.
DESCRIPTIONS = {
    "Number": {"Sing": ("singular", "UD"), "Plur": ("plural", "UD"),
               "Sgtv": ("singulativo (a confirmar)", "UD"), "Col": ("coletivo (a confirmar; o UD usa `Coll`)", "CorBo")},
    "Person": {"1": ("primeira pessoa", "UD"), "2": ("segunda pessoa", "UD"), "3": ("terceira pessoa", "UD")},
    "Mood": {"Ind": ("indicativo", "UD"), "Sub": ("subjuntivo/dependente (a confirmar)", "UD"),
             "Imp": ("imperativo", "UD"), "Quot": ("quotativo (a confirmar)", "UD"),
             "Opt": ("optativo", "UD")},
    "Clusivity": {"In": ("inclusivo", "UD"), "Ex": ("exclusivo", "UD")},
    "Voice": {"Cau": ("causativo", "UD"), "Pass": ("passivo", "UD"),
              "CauPass": ("causativo-passivo (a confirmar)", "CorBo")},
    "Deixis": {"Prox": ("proximal", "UD"), "Med": ("medial", "UD"), "Dist": ("distal", "UD"),
               "Remt": ("remoto (a confirmar)", "UD")},
    "Reflex": {"Yes": ("reflexivo / correferente com o sujeito (prefixo t-) (a confirmar)", "UD")},
    "PronType": {"Art": ("artigo", "UD"), "Prs": ("pessoal", "UD"), "Int": ("interrogativo", "UD"),
                 "Dem": ("demonstrativo", "UD"), "Rcp": ("recíproco", "UD"), "Tot": ("total/coletivo", "UD"),
                 "Ind": ("indefinido", "UD")},
    "Polarity": {"Neg": ("negativo", "UD")},
    "Status": {"Irr": ("irrealis (a confirmar)", "CorBo")},
    "Nomzr": {"Rel": ("nominalização relativa (a confirmar)", "CorBo"),
              "Loc": ("nominalização locativa (a confirmar)", "CorBo")},
    "Definite": {"Ind": ("indefinido", "UD")},
    "Aspect": {"Prog": ("progressivo", "UD"), "Inc": ("incoativo (a confirmar)", "CorBo")},
    "Degree": {"Dim": ("diminutivo", "UD"), "Aug": ("aumentativo", "UD")},
    "Speech": {"Ind": ("discurso indireto (a confirmar)", "CorBo"), "Quo": ("discurso citado (a confirmar)", "CorBo"),
               "IndTrans": ("(a definir)", "CorBo")},
    "VerbForm": {"Ger": ("gerúndio/forma adverbial (a confirmar)", "UD")},
    "Person[psor]": {"1": ("possuidor de 1ª pessoa", "UD"), "2": ("possuidor de 2ª pessoa", "UD"),
                     "3": ("possuidor de 3ª pessoa", "UD")},
    "Number[psor]": {"Sing": ("possuidor singular", "UD"), "Plur": ("possuidor plural", "UD")},
    "Emph": {"Yes": ("enfático (a confirmar)", "UD")},
    "Int": {"Yes": ("interrogativo (a confirmar; considerar PronType=Int ou Mood=Int)", "CorBo")},
    "Gender": {"Fem": ("feminino (empréstimos?)", "UD"), "Masc": ("masculino (empréstimos?)", "UD")},
}
UPOS_DESC = {
    "ADJ": "adjetivo", "ADP": "posposição", "ADV": "advérbio", "AUX": "auxiliar", "CCONJ": "conjunção coordenativa",
    "DET": "determinante/artigo/demonstrativo", "INTJ": "interjeição", "NOUN": "substantivo", "NUM": "numeral",
    "PART": "partícula", "PRON": "pronome", "PROPN": "nome próprio", "PUNCT": "pontuação",
    "SCONJ": "conjunção subordinativa", "SYM": "símbolo", "VERB": "verbo", "X": "outro / não classificado",
}


def main():
    feats = collections.defaultdict(collections.Counter)
    upos, deprel, xpos = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
    for line in CONLLU.read_text(encoding="utf-8").split("\n"):
        f = line.split("\t")
        if line.startswith("#") or len(f) != 10:
            continue
        upos[f[3]] += 1
        deprel[f[7]] += 1
        xpos[f[4]][f[3]] += 1
        if f[5] != "_":
            for kv in f[5].split("|"):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    feats[k][v] += 1

    inventory = {}
    for k in sorted(set(feats) | set(DESCRIPTIONS)):
        vals = {}
        for v in sorted(set(feats.get(k, {})) | set(DESCRIPTIONS.get(k, {}))):
            n = feats.get(k, {}).get(v, 0)
            desc = DESCRIPTIONS.get(k, {}).get(v)
            if desc or (n >= MIN_COUNT and k[:1].isupper() and v[:1].isalnum()):
                vals[v] = {"count": n, "description": desc[0] if desc else "(sem descrição)",
                           "origin": desc[1] if desc else "CorBo"}
        if vals:
            inventory[k] = {"values": vals}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"source": str(CONLLU.relative_to(ROOT)), "min_count": MIN_COUNT,
                                    "features": inventory}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = ["# Inventário de rótulos do CorBo", "",
          "> Gerado automaticamente por `scripts/build_annotation_inventory.py` a partir de "
          "`CorBo/Corpus_Files/CorBo.conllu`. Não edite à mão; edite as descrições no script.", "",
          "Descrições marcadas *(a confirmar)* são rascunhos que dependem de revisão linguística.", "",
          "## UPOS", "", "| UPOS | Descrição | Tokens |", "|---|---|---:|"]
    for u, n in upos.most_common():
        md.append(f"| `{u}` | {UPOS_DESC.get(u, '**fora do UD — revisar**')} | {n} |")
    md += ["", "## XPOS (rótulos do projeto) → UPOS", "", "| XPOS | UPOS observados |", "|---|---|"]
    for x, c in sorted(xpos.items(), key=lambda z: -sum(z[1].values())):
        md.append(f"| `{x}` | " + ", ".join(f"`{u}` ({n})" for u, n in c.most_common()) + " |")
    md += ["", "## DEPREL", "", "| DEPREL | Tokens |", "|---|---:|"]
    for d, n in deprel.most_common():
        md.append(f"| `{d}` | {n} |")
    md += ["", "## FEATS", "", "| Traço | Valor | Origem | Descrição | Tokens |", "|---|---|---|---|---:|"]
    for k, data in inventory.items():
        for v, info in data["values"].items():
            md.append(f"| `{k}` | `{v}` | {info['origin']} | {info['description']} | {info['count']} |")
    rare = [(k, v, n) for k, c in feats.items() for v, n in c.items()
            if k not in inventory or v not in inventory[k]["values"]]
    if rare:
        md += ["", "## Valores raros ou não documentados (revisar)", "", "| Traço | Valor | Tokens |", "|---|---|---:|"]
        for k, v, n in sorted(rare):
            md.append(f"| `{k}` | `{v}` | {n} |")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("Inventário:", OUT_JSON, "|", OUT_MD, "|", sum(len(d["values"]) for d in inventory.values()), "valores")


if __name__ == "__main__":
    main()
