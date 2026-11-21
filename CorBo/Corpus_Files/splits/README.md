# Camadas derivadas do CoNLL-U

Derivado de CorBo/Corpus_Files/CorBo.conllu por scripts/split_gold_silver.py — não editar.

- `CorBo.gold.conllu`: sentenças com anotação inteiramente manual, sintaxe completa e sem erros estruturais.
- `CorBo.silver.conllu`: sentenças estruturalmente válidas que contêm anotação automática (`Auto=`).
- `review_sentences.tsv`: sentenças tokenizadas que precisam de revisão (erros ou sintaxe incompleta).

Unidades sem tokens (pendentes de tokenização) não entram em nenhuma camada.
