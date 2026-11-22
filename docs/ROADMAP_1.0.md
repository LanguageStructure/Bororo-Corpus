# Critérios para o CorBo 1.0

A versão 1.0 promete estabilidade. Depois dela, os `sent_id`, o formato e as convenções de tokenização
só mudam em versões maiores (2.0). Os critérios abaixo precisam estar cumpridos antes da 1.0.

| # | Critério | Situação na v0.10.0 |
|---|---|---|
| 1 | Traduções (`# text_por`) revisadas e alinhadas às sentenças | em revisão manual (FFG) |
| 2 | Ética e direitos preenchidos: consentimento e seu registro, comitê de ética, direitos das traduções bíblicas e dos materiais de arquivo, contato | parcial (`docs/ETICA_E_GOVERNANCA.md`) |
| 3 | Nenhuma divergência entre `# text` e tokens | 116 (`CorBo/validation/texto_tokens_revisao.tsv`) |
| 4 | Nenhum erro de validação, inclusive na camada silver | 706 (gold: 0) |
| 5 | Decisões ortográficas fechadas (`docs/ORTOGRAFIA.md`) | 3 pontos abertos, mais a revisão dos acentos |
| 6 | Valores de traço raros decididos (`Mood=Qop/Qot/Imd/In`, `Number=Col`, `Voice=CPass`) | abertos |
| 7 | Proveniência de todos os grupos de `sent_id` (`CorBo/validation/sent_id_groups.tsv`) | parcial |
| 8 | Compromisso de estabilidade dos `sent_id` documentado | a fazer |

Opcional, mas recomendado: camada gold aprovada no validador oficial do Universal Dependencies
(`tools/validate.py`) e submissão do treebank ao UD; avaliação do tokenizador com o gold de segmentação.
