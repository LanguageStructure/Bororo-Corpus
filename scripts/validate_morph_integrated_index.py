#!/usr/bin/env python3
"""Valida índice morfológico integrado antes de sua publicação no site.

Uso: python3 scripts/validate_morph_integrated_index.py
"""
import json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"docs/data/morph-integrated-index.json"
def main():
    if not PATH.exists():
        sys.exit("Índice ausente. Execute: python3 scripts/build_morph_integrated_index.py")
    obj=json.loads(PATH.read_text(encoding="utf-8"))
    assert obj.get("schema")=="corbo-morph-integrated/v1","schema incorreto"
    entries=obj["entries"]
    assert entries,"Índice vazio: não publique. Regenere após corrigir a leitura do CoNLL-U."
    forms=[x["form"] for x in entries]
    assert len(forms)==len(set(forms)),"formas duplicadas"
    assert all(isinstance(x["frequency"],int) and x["frequency"]>0 for x in entries),"frequência inválida"
    assert len(entries)==obj["stats"]["types"],"contagem de tipos divergente"
    assert sum(x["frequency"] for x in entries)==obj["stats"]["tokens"],"contagem de tokens divergente"
    statuses=Counter()
    for entry in entries:
        for lex in entry["lexical_evidence"]:
            assert lex["frequency"]>0,"frequência lexical inválida"
            assert isinstance(lex["lemma"],str),"lema inválido"
        for morph in entry["morphological_segmentations"]:
            assert morph["status"] in ("confirmed","hypothesis"),"status inválido"
            assert morph["segments"] and all(isinstance(s,str) and s for s in morph["segments"]),"segmentos inválidos"
            statuses[morph["status"]]+=1
            if morph["surface_matches"]:
                assert "".join(morph["segments"])==entry["form"],"reconstrução incorreta"
    report={"valid":True,"types":len(entries),"tokens":sum(x["frequency"] for x in entries),
            "types_with_lexical_evidence":sum(bool(x["lexical_evidence"]) for x in entries),
            "types_with_segmentation":sum(bool(x["morphological_segmentations"]) for x in entries),
            "segmentations_by_status":dict(statuses),
            "file_bytes":PATH.stat().st_size}
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
