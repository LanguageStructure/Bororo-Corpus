# Protocolo de avaliação do tokenizador CorBo

## Objetivo

Separar cobertura, consistência com análises já revisadas e generalização para formas não utilizadas no desenvolvimento. Nenhuma dessas medidas deve ser chamada de acurácia independente sem um conjunto de referência mantido fora do desenvolvimento.

## Congelamento

Antes da amostragem, registrar o commit do código, a versão do modelo, os arquivos CoNLL-U utilizados e a semente aleatória. Não alterar as regras com base nas formas do teste até registrar a primeira avaliação.

## Exclusões

O comando abaixo exclui formas presentes nos paradigmas revisados e permite excluir outras formas já utilizadas na elaboração das regras. A lista adicional deve incluir exemplos consultados manualmente, testes unitários e formas usadas na depuração.

```bash
git rev-parse HEAD
python3 scripts/train_tokenizer.py
python3 scripts/prepare_tokenizer_gold.py --size 150 --seed 20261020 --exclude-reviewed --exclude development_forms.txt --output tokenizer_gold_review.csv
```

Se não houver uma lista adicional, omitir `--exclude development_forms.txt`; nesse caso a independência ainda não está demonstrada. A exclusão de formas idênticas também não elimina vazamento entre membros de um mesmo paradigma ou entre sentenças relacionadas.

## Revisão cega

O revisor preenche `segments` com segmentos de superfície separados por `+`, por exemplo `ik + ie`, sem consultar as previsões do modelo. Marcar `review_status=approved` somente após revisão; manter `pending` em casos incertos. Guardar separadamente a notação linguística com parênteses, quando necessária. Não incorporar as formas aprovadas ao treinamento antes da avaliação inicial.

## Conversão e avaliação

```bash
python3 scripts/convert_tokenizer_gold.py tokenizer_gold_review.csv --output tokenizer_gold.json --require-all
python3 scripts/evaluate_tokenizer.py --gold tokenizer_gold.json --output tokenizer_evaluation.json
python3 scripts/tokenizer_error_report.py --gold tokenizer_gold.json --output tokenizer_error_report.csv
```

Relatar número de itens, proporção analisada, correspondência exata sobre todos os itens, correspondência exata condicionada a uma previsão e distribuição dos erros de fronteira. A amostra estratificada **não** é representativa da distribuição natural do corpus; não extrapolar sua acurácia diretamente para todos os tokens.

## Limitações

O modelo pode já ter visto os tipos do conjunto de teste no corpus usado para treinar o léxico. Excluir formas da revisão não equivale a removê-las do treinamento. Para um teste rigorosamente fora da amostra, separar documentos ou famílias lexicais antes de construir o modelo, reconstruir o modelo sem o conjunto reservado e avaliar apenas no conjunto reservado. Documentar a unidade de separação escolhida.
