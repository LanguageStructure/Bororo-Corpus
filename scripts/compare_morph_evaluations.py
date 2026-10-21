#!/usr/bin/env python3
"""Compara avaliações held-out dos dois baselines sem confundir cobertura e acerto.

Uso: python3 scripts/compare_morph_evaluations.py
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES={
    "orthographic":ROOT/"tokenizer_morph_similarity_evaluation.json",
    "affix_aware":ROOT/"tokenizer_morph_rule_evaluation.json",
}
def load(path):
    obj=json.loads(path.read_text(encoding="utf-8"))
    rows={}
    for r in obj["predictions"]:
        key=(r["gold_lemma"],r["form"])
        if key in rows:
            raise ValueError("Duplicated test item: "+repr(key))
        rows[key]=r
    return rows
def metrics(rows):
    n=len(rows);tok=sum(int(r["frequency"]) for r in rows.values())
    covered=[r for r in rows.values() if r["predicted_lemma"] is not None]
    correct=[r for r in rows.values() if r["predicted_lemma"]==r["gold_lemma"]]
    return {
        "test_types":n,"test_tokens":tok,
        "covered_types":len(covered),"correct_types":len(correct),
        "incorrect_types":len(covered)-len(correct),
        "abstained_types":n-len(covered),
        "type_coverage":len(covered)/n if n else None,
        "type_precision":len(correct)/len(covered) if covered else None,
        "type_accuracy_including_abstentions":len(correct)/n if n else None,
        "token_coverage":sum(int(r["frequency"]) for r in covered)/tok if tok else None,
        "token_accuracy_including_abstentions":sum(int(r["frequency"]) for r in correct)/tok if tok else None,
    }
def main():
    data={name:load(path) for name,path in FILES.items()}
    keys=set(next(iter(data.values())))
    if any(set(rows)!=keys for rows in data.values()):
        raise SystemExit("ERRO: os modelos não usam o mesmo conjunto de teste.")
    for key in keys:
        freqs={int(rows[key]["frequency"]) for rows in data.values()}
        if len(freqs)!=1:raise SystemExit("ERRO: frequência divergente em "+repr(key))
    report={"schema":"corbo-morph-baseline-comparison/v1",
            "models":{name:metrics(rows) for name,rows in data.items()},
            "per_form":[],"methodological_notes":[
                "Comparação pareada: mesmas 20 formas e frequências.",
                "Acurácia com abstenções considera ausência de previsão como não acerto.",
                "Sem conjunto de desenvolvimento separado, não ajustar regras olhando para estes itens de teste.",
                "Resultados estimam apenas lematização de cinco verbos; não avaliam segmentação, FEATS nem tokenização.",
                "Amostra pequena, desbalanceada e extraída do mesmo corpus; não é avaliação externa."
            ]}
    for lemma,form in sorted(keys):
        item={"lemma":lemma,"form":form,"frequency":next(iter(data.values()))[(lemma,form)]["frequency"]}
        for name,rows in data.items():
            r=rows[(lemma,form)]
            item[name]={"predicted":r["predicted_lemma"],"correct":r["predicted_lemma"]==lemma}
        report["per_form"].append(item)
    out=ROOT/"tokenizer_morph_comparison.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report["models"],ensure_ascii=False,indent=2))
    print("\nDivergências entre os modelos:")
    for r in report["per_form"]:
        a=r["orthographic"];b=r["affix_aware"]
        if a!=b:
            print("{lemma:7} {form:22} n={frequency:3} ort={ort} morf={morf}".format(
                **r,ort=a["predicted"] or "ABSTENÇÃO",morf=b["predicted"] or "ABSTENÇÃO"))
    print("\nRelatório:",out.name)
if __name__=="__main__":main()
