#!/usr/bin/env python3
"""Analisador unificado: morfotática, alomorfia e evidência em camadas.

Mantém análises confirmadas separadas das hipóteses. Não usa o teste
held-out para alegar desempenho preditivo. Não infere FEATS.
Uso: python3 scripts/morph_analyzer_v2.py --form itumodukare
"""
import argparse,json
from pathlib import Path

# Evidências manuais confirmadas; podem divergir da concatenação superficial.
CONFIRMED={
    "iture":[{"lemma":"tu","segments":["i","tu","re"]}],
    "akodure":[{"lemma":"kodu","segments":["a","kodu","re"]}],
    "icare":[{"lemma":"ca","segments":["i","ca","re"]}],
    "iwiegare":[{"lemma":"biega","segments":["i","wiega","re"]}],
    "ire":[{"lemma":"re","segments":["i","re"]}],
    "padui":[{"lemma":"tu","segments":["pa","tu","i"]}],
    "tududo":[{"lemma":"tu","segments":["tu","tu","do"]}],
    "akore":[{"lemma":"ako","segments":["ako","re"]}],
    "inagore":[{"lemma":"ako","segments":["i","nago","re"]}],
    "egore":[{"lemma":"ako","segments":["e","ako","re"]}],
    "cedure":[{"lemma":"tu","segments":["ce","du","re"]}],
    "ure":[{"lemma":"re","segments":["u","re"]}],
    "cenagore":[{"lemma":"ako","segments":["cen","ako","re"]}],
    "makore":[{"lemma":"mako","segments":["mako","re"]}],
    "cegodure":[{"lemma":"kodu","segments":["ce","kodu","re"]}],
    "aregodure":[{"lemma":"regodu","segments":["a","regodu","re"]}],
    "cedaregodure":[{"lemma":"aregodu","segments":["ce","are","godu","re"],"surface_segments":["ced","are","godu","re"],"morphophonology":"ce → ced (alomorfia contextual; d não é morfema independente)"}],
    "cegodo":[{"lemma":"kodo","segments":["ce","kodo"]}],
}
# Cada alternante é uma hipótese explícita, não uma regra universal.
ALLOMORPHS={
    "tu":("tu","du"),
    "mako":("mako","mago"),
    "ako":("ako","ago","nago"),
    "kodu":("kodu","godu"),
    "mugu":("mugu",),
}
PREFIXES=("ce","pa","ta","et","tu","i","a","e","")
# Conflitos atestados: não propor automaticamente uma base verbal.
# A forma continua consultável por sua anotação lexical CoNLL-U.
REVIEW_REQUIRED={"ituiagu"}
# Morfotática: terminações superficiais e análises propostas.
ENDINGS={
    "modukare":("modu","ka","re"),
    "modukana":("modu","kana"),
    "modukae":("modu","kae"),
    "moduie":("modu","ie"),
    "modu":("modu",),
    "mode":("mode",),
    "nure":("nu","re"),
    "kare":("ka","re"),
    "iagu":("iagu",),
    "wo":("wo",),
    "re":("re",),
    "ie":("ie",),
    "ia":("ia",),
    "i":("i",),
    "do":("do",),
    "du":("du",),
    "":(),
}
def analyze(form):
    surface=form.casefold()
    analyses=[]
    for item in CONFIRMED.get(surface,[]):
        parts=item["segments"]
        analyses.append({"lemma":item["lemma"],"segments":parts,
                         "status":"confirmed","surface_matches":"".join(parts)==surface,
                         **({"surface_segments":item["surface_segments"]} if "surface_segments" in item else {}),
                         **({"morphophonology":item["morphophonology"]} if "morphophonology" in item else {})})
    if surface in REVIEW_REQUIRED:
        return {"form":form,"analyses":analyses,
                "review_required":True,
                "note":"Conflito de lema no CoNLL-U: hipótese verbal automática suspensa até revisão linguística."}
    for lemma,stems in ALLOMORPHS.items():
        for prefix in PREFIXES:
            if not surface.startswith(prefix):
                continue
            remainder=surface[len(prefix):]
            for stem in stems:
                if not remainder.startswith(stem):
                    continue
                ending=remainder[len(stem):]
                if ending not in ENDINGS:
                    continue
                parts=([prefix] if prefix else [])+[stem]+list(ENDINGS[ending])
                proposal={"lemma":lemma,"segments":parts,"status":"hypothesis",
                          "surface_matches":"".join(parts)==surface,
                          "allomorph":stem if stem!=lemma else None}
                if not any(a["lemma"]==lemma and a["segments"]==parts for a in analyses):
                    analyses.append(proposal)
    analyses.sort(key=lambda a:(a["status"]!="confirmed",a["lemma"],len(a["segments"]),a["segments"]))
    return {"form":form,"analyses":analyses,"review_required":False,
            "note":"Hipóteses de superfície, sem FEATS; análises confirmadas têm precedência."}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--form",required=True)
    args=p.parse_args()
    print(json.dumps(analyze(args.form),ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
