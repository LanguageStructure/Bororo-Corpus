#!/usr/bin/env python3
"""Composição de sufixos verbais atestados/hipotéticos, sem atribuir FEATS não validados.

Uso: python3 scripts/morph_suffixes.py --form itumodukare
     python3 scripts/morph_suffixes.py --form imagomodukare
"""
import argparse,json
from functools import lru_cache
# Sufixos maiores têm decomposições explícitas; 'mode' é variante superficial
# e NÃO deve ser automaticamente identificado com 'modu+re'.
PATTERNS={
 "modukare":("modu","ka","re"),
 "modukae":("modu","kae"),
 "modukana":("modu","kana"),
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
# Bases e prefixos são provisórios e devem ser cotejados com os paradigmas.
STEMS={"tu":("tu","du"),"mako":("mako","mago"),
       "ako":("ako","ago","nago"),"kodu":("kodu","godu"),"mugu":("mugu",)}
PREFIXES=("ce","pa","ta","et","tu","i","a","e","")
def analyze(form):
    word=form.casefold();out=[]
    for lemma,allomorphs in STEMS.items():
        for prefix in PREFIXES:
            if not word.startswith(prefix):continue
            rem=word[len(prefix):]
            for stem in allomorphs:
                if not rem.startswith(stem):continue
                tail=rem[len(stem):]
                if tail not in PATTERNS:continue
                parts=([prefix] if prefix else [])+[stem]+list(PATTERNS[tail])
                out.append({"lemma":lemma,"segments":parts,"status":"hypothesis",
                            "surface_matches":"".join(parts)==word,
                            "surface_suffix":tail,"stem_allomorph":stem})
    out.sort(key=lambda x:(x["lemma"],len(x["segments"]),x["segments"]))
    return {"form":form,"analyses":out,
            "note":"Decomposição composicional hipotética; não atribui FEATS nem valida alomorfia."}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--form",required=True)
    args=p.parse_args();print(json.dumps(analyze(args.form),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
