#!/usr/bin/env python3
"""Prioriza revisão de formas frequentes sem segmentação confirmada.

Uso: python3 scripts/prepare_morph_review_queue.py
Saída local: tokenizer_morph_review_queue.tsv
Não altera o corpus nem promove hipóteses a análises confirmadas.
"""
import argparse,csv,json,unicodedata
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"docs/data/morph-integrated-index.json"
OUT=ROOT/"tokenizer_morph_review_queue.tsv"
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--index',type=Path,default=INDEX)
    p.add_argument('--output',type=Path,default=OUT)
    p.add_argument('--top',type=int,default=100,help='Número máximo de formas (0=todas)')
    p.add_argument('--frequency-first',action='store_true',help='Ordenar por frequência absoluta')
    args=p.parse_args()
    data=json.loads(args.index.read_text(encoding="utf-8"))
    if not data.get("entries"):
        raise RuntimeError("Índice vazio. Gere e valide primeiro.")
    rows=[]
    excluded_punctuation=0
    for entry in data["entries"]:
        form=entry["form"]
        if not any(unicodedata.category(ch).startswith("L") for ch in form):
            excluded_punctuation+=1
            continue
        analyses=entry["morphological_segmentations"]
        if any(a["status"]=="confirmed" for a in analyses):
            continue
        evidence=entry["lexical_evidence"]
        lexical=sum(x["frequency"] for x in evidence)
        verb_tokens=sum(x["frequency"] for x in evidence if x["upos"]=="VERB")
        nonverb_tokens=sum(x["frequency"] for x in evidence if x["upos"] not in ("VERB",None))
        if not lexical:
            group="sem_lema_anotado"
        elif verb_tokens > nonverb_tokens and verb_tokens >= 2:
            group="verbo_predominante"
        elif verb_tokens and nonverb_tokens and verb_tokens <= nonverb_tokens:
            group="categoria_mista"
        else:
            group="outra_categoria"
        rows.append({
            "form":entry["form"],"tokens":entry["frequency"],
            "priority_group":group,
            "verb_tokens":verb_tokens,"nonverb_tokens":nonverb_tokens,
            "lexically_annotated_tokens":lexical,
            "attested_lemmas":" | ".join(sorted({x["lemma"] for x in evidence})),
            "attested_upos":" | ".join(sorted({x["upos"] or "_" for x in evidence})),
            "proposed_segmentations":" | ".join(
                "+".join(a["segments"]) for a in analyses if a["status"]=="hypothesis"
            ),
            "reviewed_segments":"","reviewed_stem":"","review_status":"","review_note":""
        })
    rank={"verbo_predominante":0,"categoria_mista":1,"outra_categoria":2,"sem_lema_anotado":3}
    if args.frequency_first:
        rows.sort(key=lambda r:(-int(r["tokens"]),r["form"]))
    else:
        rows.sort(key=lambda r:(rank[r["priority_group"]],-int(r["tokens"]),r["form"]))
    if args.top < 0:
        p.error("--top deve ser >= 0")
    if args.top:
        rows=rows[:args.top]
    fields=["form","tokens","priority_group","verb_tokens","nonverb_tokens","lexically_annotated_tokens",
            "attested_lemmas","attested_upos","proposed_segmentations",
            "reviewed_segments","reviewed_stem","review_status","review_note"]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t")
        w.writeheader();w.writerows(rows)
    print("Formas para revisão:",len(rows))
    print("Pontuação/símbolos excluídos:",excluded_punctuation)
    for group in rank:
        items=[r for r in rows if r["priority_group"]==group]
        print("\n"+group+": "+str(len(items)))
        for r in items[:12]:
            print(" ",r["form"],"n="+str(r["tokens"]),"lemas="+(r["attested_lemmas"] or "—"),
                  "hipótese="+(r["proposed_segmentations"] or "—"))
    print("\nArquivo:",args.output)
if __name__=="__main__":main()
