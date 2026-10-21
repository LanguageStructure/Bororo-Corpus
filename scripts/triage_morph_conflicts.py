#!/usr/bin/env python3
"""Triagem de conflitos e hipóteses sem evidência verbal no CorBo.

Cruza a auditoria com ocorrências reais do CoNLL-U e apresenta contextos
sem pressupor que divergências de lema sejam erros.
Uso: python3 scripts/triage_morph_conflicts.py
"""
import csv,json
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"tokenizer_morph_analyzer_audit.tsv"
CORPUS=ROOT/"CorBo/Corpus_Files/CorBo.conllu"
OUTPUT=ROOT/"tokenizer_morph_conflict_triage.tsv"
def main():
    with AUDIT.open(encoding="utf-8",newline="") as f:
        rows=[r for r in csv.DictReader(f,delimiter="\t")
              if r["status"] in ("lemma_conflict","no_verbal_lemma_evidence")]
    targets={r["form"] for r in rows}
    evidence=defaultdict(lambda:{"annotations":Counter(),"contexts":[]})
    sent_id=text="";tokens=[]
    def flush():
        if not tokens:return
        for form,lemma,upos,feats in tokens:
            if form not in targets:continue
            entry=evidence[form]
            entry["annotations"][(lemma,upos,feats)]+=1
            if len(entry["contexts"])<3:
                entry["contexts"].append({"sent_id":sent_id,"text":text})
    with CORPUS.open(encoding="utf-8-sig") as f:
        for line in f:
            line=line.rstrip("\r\n")
            if not line:
                flush();sent_id=text="";tokens=[]
            elif line.startswith("# sent_id ="):
                sent_id=line.split("=",1)[1].strip()
            elif line.startswith("# text ="):
                text=line.split("=",1)[1].strip()
            elif not line.startswith("#"):
                c=line.split("\t")
                if len(c)==10 and c[0].isdigit():
                    tokens.append((c[1].casefold(),c[2],c[3],c[5]))
        flush()
    out=[]
    for r in rows:
        ev=evidence[r["form"]]
        annotations=sorted(ev["annotations"].items(),key=lambda x:(-x[1],x[0]))
        out.append({
            "form":r["form"],"status":r["status"],"tokens":r["tokens"],
            "proposed_lemmas":r["proposed_lemmas"],
            "attested_verb_lemmas":r["attested_verb_lemmas"],
            "attested_annotations":json.dumps([
                {"lemma":lemma,"upos":upos,"feats":feats,"n":n}
                for (lemma,upos,feats),n in annotations[:12]],ensure_ascii=False),
            "contexts":json.dumps(ev["contexts"],ensure_ascii=False)
        })
    out.sort(key=lambda r:(r["status"]!="lemma_conflict",-int(r["tokens"]),r["form"]))
    with OUTPUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]) if out else
            ["form","status","tokens","proposed_lemmas","attested_verb_lemmas","attested_annotations","contexts"],delimiter="\t")
        w.writeheader();w.writerows(out)
    print("Conflitos e hipóteses sem evidência verbal:",len(out))
    for r in out[:20]:
        annotations=json.loads(r["attested_annotations"])
        short=", ".join("%s/%s:%s"%(a["lemma"],a["upos"],a["n"]) for a in annotations[:3])
        print("%-22s %5s %-26s proposta=%-15s atestado=%s"%(r["form"],r["tokens"],r["status"],r["proposed_lemmas"],short))
    print("Relatório detalhado:",OUTPUT.name)
if __name__=="__main__":main()
