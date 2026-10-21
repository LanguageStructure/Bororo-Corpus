#!/usr/bin/env python3
"""Protótipo conservador de análise morfofonológica do Bororo.

As regras são explícitas e têm status 'hypothesis'; análises confirmadas
são registradas separadamente. Não confundir com o teste held-out anterior.

Uso:
 python3 scripts/morphophonology.py --form iture
 python3 scripts/morphophonology.py --form cedure
 python3 scripts/morphophonology.py --form imagore
 python3 scripts/morphophonology.py --form ikodure
"""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Análises diretamente confirmadas no diálogo de revisão, sem inventar FEATS.
CONFIRMED={
 "iture":("tu",["i","tu","re"]),
 "icare":("ca",["i","ca","re"]),
 "ire":("re",["i","re"]),
 "akodure":("kodu",["a","kodu","re"]),
 "iwiegare":("biega",["i","wiega","re"]),
}
# Correspondências superficiais; a alomorfia precisa de validação.
STEMS={"tu":("tu","du"),"mako":("mako","mago"),"ako":("ako","ago","nago"),
       "kodu":("kodu","godu"),"mugu":("mugu",)}
PREFIXES=("ce","pa","ta","et","tu","i","a","e","")
SUFFIXES=("modukare","modukana","moduie","modukae","modu","mode","nure","kare","iagu","wo","re","do","du","i","")
def analyze(form):
    word=form.casefold()
    results=[]
    if word in CONFIRMED:
        lemma,segments=CONFIRMED[word]
        results.append({"lemma":lemma,"morphemes":segments,"status":"confirmed",
                        "surface_reconstruction":"".join(segments)==word})
    for lemma,stems in STEMS.items():
        for prefix in PREFIXES:
            if not word.startswith(prefix):continue
            remainder=word[len(prefix):]
            for stem in stems:
                if not remainder.startswith(stem):continue
                tail=remainder[len(stem):]
                if tail not in SUFFIXES:continue
                seg=[s for s in (prefix,stem,tail) if s]
                candidate={"lemma":lemma,"morphemes":seg,"status":"hypothesis",
                           "surface_reconstruction":"".join(seg)==word,
                           "allomorph":stem if stem!=lemma else None}
                if candidate not in results:results.append(candidate)
    results.sort(key=lambda r:(r["status"]!="confirmed",r["lemma"],len(r["morphemes"])))
    return {"form":form,"analyses":results,
            "note":"Hipóteses não equivalem a segmentações validadas; ausência de análise é permitida."}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--form",required=True)
    args=p.parse_args()
    print(json.dumps(analyze(args.form),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
