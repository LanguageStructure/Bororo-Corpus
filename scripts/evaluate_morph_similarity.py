#!/usr/bin/env python3
"""Baseline de generalização por distância de edição; NÃO é segmentação morfológica.

Recria exatamente a partição de evaluate_morph_heldout.py e exclui
globalmente TODAS as formas reservadas do treinamento (evita vazamento
quando uma forma aparece associada a mais de um lema).
Uso: python3 scripts/evaluate_morph_similarity.py
"""
import csv,json,random
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET={"tu","mako","ako","kodu","mugu"}
def distance(a,b):
    row=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        new=[i]
        for j,cb in enumerate(b,1):
            new.append(min(new[-1]+1,row[j]+1,row[j-1]+(ca!=cb)))
        row=new
    return row[-1]
def main():
    groups=defaultdict(lambda:defaultdict(int))
    with (ROOT/"tokenizer_morph_paradigms.tsv").open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f,delimiter="\t"):
            if r["lemma"] in TARGET and r["upos"]=="VERB":
                groups[r["lemma"]][r["form"]]+=int(r["frequency"])
    rng=random.Random(20261021);test=[]
    for lemma,forms in sorted(groups.items()):
        keys=sorted(forms);rng.shuffle(keys)
        n=max(1,len(keys)//5) if len(keys)>1 else 0
        test.extend((lemma,form,forms[form]) for form in sorted(keys[:n]))
    heldout_forms={form for _,form,_ in test}
    train={lemma:{form for form in forms if form not in heldout_forms} for lemma,forms in groups.items()}
    results=[];correct=covered=weighted_correct=weighted_covered=0
    for lemma,form,n in test:
        scored=[(distance(form,other),candidate,other) for candidate,forms in train.items() for other in forms]
        if not scored:
            best=[];d=None
        else:
            d=min(x[0] for x in scored)
            best=sorted({x[1] for x in scored if x[0]==d})
        # Abstenção em empates; distância <= 2 é limiar conservador
        pred=best[0] if len(best)==1 and d<=2 else None
        ok=pred==lemma
        correct+=ok;covered+=pred is not None
        weighted_correct+=n*ok;weighted_covered+=n*(pred is not None)
        results.append({"form":form,"gold_lemma":lemma,"frequency":n,"predicted_lemma":pred,
                        "nearest_distance":d,"tied_lemmas":best,"correct":ok})
    total=sum(x[2] for x in test)
    summary={"schema":"corbo-morph-similarity/v1","method":"nearest training surface form by Levenshtein distance; abstain if tie or distance > 2",
             "seed":20261021,"heldout_types":len(test),"heldout_tokens":total,
             "correct_types":correct,"covered_types":covered,
             "type_accuracy_with_abstention":correct/len(test) if test else None,
             "type_coverage":covered/len(test) if test else None,
             "type_precision_when_predicted":correct/covered if covered else None,
             "token_accuracy_with_abstention":weighted_correct/total if total else None,
             "token_coverage":weighted_covered/total if total else None,
             "warning":"Baseline ortográfico, não análise morfológica; formas de teste excluídas globalmente do treinamento; FEATS e segmentação não são previstos."}
    out=ROOT/"tokenizer_morph_similarity_evaluation.json"
    out.write_text(json.dumps({"summary":summary,"predictions":results},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("Previsões:",out.name)
if __name__=="__main__":main()
