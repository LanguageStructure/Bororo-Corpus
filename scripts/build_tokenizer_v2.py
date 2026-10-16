#!/usr/bin/env python3
"""Conservative Bororo morphology v2: attested lexicon + explicit rules.

This module does NOT infer gold morpheme boundaries from CoNLL-U columns.
It emits confirmed analyses for a small curated inventory and proposed
analyses only when the surface stem is supported by corpus lemma evidence.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import argparse, json

CONFIRMED = {
    "ure": ("u","re"), "ire": ("i","re"), "are": ("a","re"),
    "cere": ("ce","re"), "pare": ("pa","re"), "tare": ("ta","re"),
    "ere": ("e","re"), "nure": ("nu","re"),
    "imode": ("i","modu","re"), "iere": ("i","ie","re"),
    "iorudukare": ("i","jorudu","ka","re"),
    "iorudumodukare": ("i","jorudu","modu","ka","re"),
    "akore": ("ako","re"), "kururogu": ("kuru","rogu"),
    "imago": ("i","mago"), "amago": ("a","mago"),
    "pamago": ("pa","mago"), "cemago": ("ce","mago"),
    "tamago": ("ta","mago"), "emago": ("e","mago"),
    "tumago": ("tu","mago"), "iwiapagare": ("i","wiapaga","re"),
}
# Confirmed closed-class personal forms. These are whole-form rules,
# not productive stripping of arbitrary lexical stems.
PERSON_TAILS = {
    "re": ("re",), "wo": ("wo",), "ia": ("ia",),
    "ie": ("ie",), "iagu": ("iagu",),
    "kare": ("ka","re"), "kawo": ("ka","wo"),
    "kae": ("ka","e"), "kai": ("ka","i"),
    "mode": ("modu","re"), "modure": ("modu","re"),
    "modukare": ("modu","ka","re"),
    "modukae": ("modu","ka","e"), "moduie": ("modu","ie"),
    "nure": ("nu","re"),
}
PERSON_PREFIXES = ("u","i","a","e")

PREFIXES = ("ce","pa","ta","tu","et","i","a","u","e")
ENDINGS = (
    ("modu","ka","re"), ("modu","re"), ("modu","ka","wo"),
    ("ka","re"), ("ka","wo"), ("iagu",), ("ie",),
    ("wo",), ("ia",), ("re",), ("rogu",),
)
ALLOMORPHS = {"mago": "mako", "wiapaga": "biapaga", "wai": "bai"}
BLOCKED = {"tabiapagado","ibiapagare"}
PROTECTED = {"mode","modure"}

def corpus_lexicon(path):
    forms, lemmas, families = Counter(), Counter(), defaultdict(Counter)
    for line in path.open(encoding="utf-8-sig"):
        if not line or line.startswith("#"): continue
        cols=line.rstrip("\n").split("\t")
        if len(cols)!=10 or not cols[0].isdigit(): continue
        form, lemma=cols[1].casefold(),cols[2].casefold()
        if form=="_": continue
        forms[form]+=1
        if lemma!="_":
            lemmas[lemma]+=1
            families[lemma][form]+=1
    return forms,lemmas,families

def analyse(word, forms, lemmas, families):
    w=word.casefold()
    if w in BLOCKED: return {"form":word,"segments":[word],"status":"blocked"}
    # The mako paradigm is a closed, linguistically verified alternation.
    # Do not infer unattested combinations by applying k -> g globally.
    mako_prefixes = ("i", "a", "pa", "ce", "ta", "e", "tu")
    if w == "mako":
        return {"form":word,"segments":[word],"status":"confirmed","lemma":"mako"}
    for person in mako_prefixes:
        if w == person + "mago":
            return {"form":word,"segments":[person,"mago"],
                    "status":"confirmed","lemma":"mako",
                    "rule":"mako: bound mago after personal prefix"}
    # Confirmed b ~ w alternation under the 1SG prefix i-.
    # Keep the surface segmentation separate from the lexical lemma.
    if w == "iwai":
        return {"form":word,"segments":["i","wai"],
                "status":"confirmed","lemma":"bai",
                "rule":"b → w after personal prefix i"}
    # Restricted lexical alternations in the ako paradigm.
    ako_confirmed = {
        "inago": ("i(n)","ago"),
        "inagore": ("i(n)","ago","re"),
        "inagokare": ("i(n)","ago","ka","re"),
        "cenagore": ("ce(n)","ago","re"),
        "ego": ("e","go"),
        "egore": ("e","go","re"),
    }
    if w in ako_confirmed:
        return {"form":word,"segments":list(ako_confirmed[w]),
                "status":"confirmed","lemma":"ako"}
    # Avoid assigning these forms to unrelated lexical items.
    for person in PERSON_PREFIXES:
        if not w.startswith(person):continue
        tail=w[len(person):]
        if tail in PERSON_TAILS:
            return {"form":word,"segments":[person,*PERSON_TAILS[tail]],
                    "status":"confirmed","lemma":person,
                    "rule":"closed-class personal paradigm"}
    if w in CONFIRMED:
        return {"form":word,"segments":list(CONFIRMED[w]),"status":"confirmed"}
    if w in PROTECTED or w=="mago": return {"form":word,"segments":[word],"status":"unanalysed"}
    # Requiring independent lemma evidence prevents arbitrary substring splits.
    # A proposal is NOT a linguistically verified morpheme segmentation.
    options=[]
    for ending in ENDINGS:
        tail="".join(ending)
        if not w.endswith(tail) or len(w)<=len(tail)+1: continue
        stem=w[:-len(tail)]
        for prefix in ("",*PREFIXES):
            if prefix and not stem.startswith(prefix): continue
            base=stem[len(prefix):]
            if len(base)<3: continue
            # mago is a bound allomorph: only after a personal prefix.
            if base=="mago" and not prefix: continue
            # Bound allomorph must not be licensed by a bare surface form.
            if base=="mago" and prefix not in ("i","a","pa","ce","ta","e","tu"): continue
            lexical_lemma=ALLOMORPHS.get(base,base)
            if lexical_lemma not in lemmas: continue
            if not (forms[base] or families[lexical_lemma].get(w)): continue
            # Productive prefix evidence is weaker than confirmed analysis.
            parts=([prefix] if prefix else [])+[base]+list(ending)
            if "".join(parts)!=w: continue
            support=forms[base]+families[lexical_lemma].get(w,0)
            options.append((support,len(parts),parts,lexical_lemma))
    if options:
        options.sort(key=lambda x:(-x[0],x[1],x[2]))
        support,_,parts,lemma=options[0]
        return {"form":word,"segments":parts,"status":"proposed",
                "lemma":lemma,"support":support}
    return {"form":word,"segments":[word],"status":"unanalysed"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",default="CorBo/Corpus_Files/CorBo.conllu")
    ap.add_argument("--output",default="docs/data/tokenizer-v2.json")
    args=ap.parse_args()
    forms,lemmas,families=corpus_lexicon(Path(args.corpus))
    records={form:analyse(form,forms,lemmas,families) for form in sorted(forms)}
    counts=Counter(record["status"] for record in records.values())
    result={"schema":"corbo-tokenizer-v2/v1",
            "description":"Conservative analyses; proposed does not mean verified",
            "source":args.corpus,"types":len(forms),
            "tokens":sum(forms.values()),"status_counts":dict(counts),
            "analyses":records}
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print(f"{len(forms)} types; {sum(forms.values())} tokens; {dict(counts)} -> {target}")

if __name__=="__main__":main()
