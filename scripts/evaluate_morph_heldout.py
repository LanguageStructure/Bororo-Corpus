#!/usr/bin/env python3
"""Avaliação por formas não vistas para o analisador paradigmático CorBo.

Retém uma forma por lema para teste, aprende de outras formas atestadas.
O modelo baseline só reconhece formas vistas; a avaliação evita vazamento.
"""
import csv,json,random
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"tokenizer_morph_paradigms.tsv"
TARGET={"tu","mako","ako","kodu","mugu"}
def main():
    groups=defaultdict(lambda:defaultdict(int))
    with INDEX.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f,delimiter="\t"):
            if row["lemma"] in TARGET and row["upos"]=="VERB":
                groups[row["lemma"]][row["form"]]+=int(row["frequency"])
    rng=random.Random(20261021)
    train=defaultdict(set);held=[]
    for lemma,forms in sorted(groups.items()):
        keys=sorted(forms)
        rng.shuffle(keys)
        n=max(1,len(keys)//5) if len(keys)>1 else 0
        test=set(keys[:n])
        train[lemma]=set(keys[n:])
        for form in sorted(test):
            held.append({"lemma":lemma,"form":form,"frequency":forms[form],
                         "predicted_lemma":None,"correct":False})
    tokens=sum(r["frequency"] for r in held)
    result={"schema":"corbo-morph-heldout/v1","seed":20261021,
            "protocol":"20% distinct surface forms per lemma held out; training excludes their forms for that lemma",
            "heldout_types":len(held),"heldout_tokens":tokens,
            "baseline_exact_lookup_type_accuracy":0.0 if held else None,
            "baseline_exact_lookup_token_accuracy":0.0 if tokens else None,
            "caveat":"Baseline sem generalização: ausência de forma exata implica abstenção. Teste não inclui ainda regras morfofonológicas.",
            "heldout":held}
    path=ROOT/"tokenizer_morph_heldout.json"
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="heldout"},ensure_ascii=False,indent=2))
    print("Amostra de teste:",path.name)
if __name__=="__main__":main()
