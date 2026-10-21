#!/usr/bin/env python3
"""Baseline de tokenização ortográfica avaliada por fronteiras de caracteres.

Lê frases CoNLL-U e reconstrói o texto usando # text. Evita vazamento
por comparação de frases iguais: agrupa textos idênticos antes da divisão.
Não trata segmentação morfológica como tokenização ortográfica.

Uso:
  python3 scripts/evaluate_orthographic_tokenizer.py
  python3 scripts/evaluate_orthographic_tokenizer.py --limit 1000
"""
import argparse,json,re,hashlib
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
REPORT=ROOT/"tokenizer_orthographic_baseline.json"
ERRORS=ROOT/"tokenizer_orthographic_errors.tsv"

# Baseline deliberadamente simples; não separa afixos de palavras.
TOKEN_RE=re.compile(r"\w+(?:[’'-]\w+)*|[^\w\s]",re.UNICODE)

def baseline(text):
    return [(m.start(),m.end(),m.group()) for m in TOKEN_RE.finditer(text)]

def gold_spans(text,tokens):
    """Alinha tokens CoNLL-U à frase, sem inventar fronteiras."""
    pos=0;spans=[]
    for token in tokens:
        while pos<len(text) and text[pos].isspace():pos+=1
        if text.startswith(token,pos):
            spans.append((pos,pos+len(token),token));pos+=len(token)
        else:
            return None
    if text[pos:].strip():return None
    return spans

def sentences(path):
    meta={};tokens=[]
    def flush():
        if meta.get("text") and tokens:
            return (meta.get("sent_id",""),meta["text"],tokens[:])
        return None
    with path.open(encoding="utf-8-sig") as f:
        for raw in f:
            line=raw.rstrip("\r\n")
            if not line:
                result=flush()
                if result:yield result
                meta={};tokens=[]
                continue
            if line.startswith("#"):
                if "=" in line:
                    k,v=line[1:].split("=",1);meta[k.strip()]=v.strip()
            else:
                c=line.split("\t")
                if len(c)==10 and c[0].isdigit():
                    tokens.append(c[1])
        result=flush()
        if result:yield result

def boundaries(spans):
    return {end for _,end,_ in spans[:-1]}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit",type=int,default=0)
    args=ap.parse_args()
    totals=Counter();errors=[];seen=set()
    for sent_id,text,tokens in sentences(SOURCE):
        key=hashlib.sha256(text.encode("utf-8")).hexdigest()
        if key in seen:
            totals["duplicate_text"]+=1;continue
        seen.add(key)
        aligned=gold_spans(text,tokens)
        if aligned is None:
            totals["unalignable"]+=1;continue
        totals["evaluated_sentences"]+=1
        predicted=baseline(text)
        gold=boundaries(aligned);pred=boundaries(predicted)
        tp=len(gold & pred)
        totals["tp"]+=tp;totals["fp"]+=len(pred-gold);totals["fn"]+=len(gold-pred)
        if gold!=pred:
            totals["error_sentences"]+=1
            if len(errors)<200:
                errors.append((sent_id,text," | ".join(tokens),
                               " | ".join(x[2] for x in predicted),
                               ",".join(map(str,sorted(pred-gold))),
                               ",".join(map(str,sorted(gold-pred)))))
        if args.limit and totals["evaluated_sentences"]>=args.limit:break
    tp,fp,fn=totals["tp"],totals["fp"],totals["fn"]
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0
    report={"source":str(SOURCE.relative_to(ROOT)),
            "method":"regex_baseline_boundary_evaluation",
            "notes":"Somente frases alinháveis; duplicatas exatas excluídas. Não é gold revisado.",
            **dict(totals),"precision":precision,"recall":recall,"f1":f1}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with ERRORS.open("w",encoding="utf-8") as f:
        f.write("sent_id\ttext\tgold_tokens\tpredicted_tokens\textra_boundaries\tmissing_boundaries\n")
        for row in errors:
            f.write("\t".join(str(v).replace("\t"," ").replace("\n"," ") for v in row)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("Erros:",ERRORS.name)
if __name__=="__main__":main()
