#!/usr/bin/env python3
"""Exporta amostra determinística para revisão independente da tokenização.

Seleciona frases de documentos distintos quando possível, sem alterar
o corpus. A referência CoNLL-U é ocultada na planilha de revisão e
mantida em arquivo separado para auditoria; não é automaticamente gold.

Uso: python3 scripts/prepare_orthographic_gold.py --size 100 --seed 42
"""
import argparse,csv,hashlib,random
from collections import defaultdict
from pathlib import Path
from evaluate_orthographic_tokenizer import ROOT,SOURCE,sentences,baseline,gold_spans

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--size",type=int,default=100)
    ap.add_argument("--seed",type=int,default=42)
    args=ap.parse_args()
    if args.size<1:ap.error("--size deve ser positivo")
    groups=defaultdict(list);seen=set()
    for sid,text,tokens in sentences(SOURCE):
        if text in seen:continue
        seen.add(text)
        if gold_spans(text,tokens) is None:continue
        # Agrupamento aproximado por prefixo de sent_id; verificar manualmente
        # se o prefixo realmente corresponde a um documento.
        group=sid.rsplit("-",1)[0] if "-" in sid else sid
        groups[group].append((sid,text,tokens))
    rng=random.Random(args.seed)
    keys=sorted(groups)
    rng.shuffle(keys)
    for key in keys:rng.shuffle(groups[key])
    chosen=[]
    while keys and len(chosen)<args.size:
        remaining=[]
        for key in keys:
            if len(chosen)>=args.size:break
            if groups[key]:
                chosen.append(groups[key].pop())
            if groups[key]:remaining.append(key)
        keys=remaining
    review=ROOT/"tokenizer_orthographic_gold_review.tsv"
    reference=ROOT/"tokenizer_orthographic_gold_reference.tsv"
    with review.open("w",encoding="utf-8",newline="") as f,reference.open("w",encoding="utf-8",newline="") as g:
        w=csv.writer(f,delimiter="\t");r=csv.writer(g,delimiter="\t")
        w.writerow(["sent_id","text","predicted_tokens","corrected_tokens","review_status","notes"])
        r.writerow(["sent_id","text","conllu_tokens","sha256_text"])
        for sid,text,tokens in chosen:
            predicted=" | ".join(x[2] for x in baseline(text))
            w.writerow([sid,text,predicted,"","",""])
            r.writerow([sid,text," | ".join(tokens),hashlib.sha256(text.encode("utf-8")).hexdigest()])
    print("Frases selecionadas:",len(chosen))
    print("Grupos de sent_id distintos:",len({s.rsplit("-",1)[0] if "-" in s else s for s,_,_ in chosen}))
    print("Revisão:",review.name)
    print("Referência CoNLL-U (não gold):",reference.name)
    print("Instrução: preencher corrected_tokens e review_status=approved após revisão humana.")
if __name__=="__main__":main()
