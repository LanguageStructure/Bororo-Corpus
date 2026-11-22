# Validação do CoNLL-U

Arquivos gerados a partir de `CorBo/Corpus_Files/CorBo.conllu`. Veja também o [guia de anotação](../../docs/ANNOTATION_GUIDE.md).

| Arquivo | Conteúdo | Gerado por |
|---|---|---|
| `issues.tsv` | todos os problemas atuais, com linha, `sent_id`, categoria e severidade | `scripts/validate_conllu.py --report` |
| `summary.json` | contagens por categoria | `scripts/validate_conllu.py --summary` |
| `summary_before_fix.json` | contagens antes das correções seguras de 21/11/2026 | idem, sobre a versão anterior |
| `baseline.json` | linha de base usada em CI (nenhuma categoria de erro pode aumentar) | cópia de `summary.json` |
| `safe_fixes.tsv` | cada alteração automática feita em 21/11/2026 (linha, coluna, antes, depois, regra) | `scripts/fix_conllu_safe.py --log` |
| `feature_inventory.json` | traços e valores documentados (o validador avisa sobre os demais) | `scripts/build_annotation_inventory.py` |
| `sent_id_groups.tsv` | grupos de `sent_id` com contagens e colunas **a preencher** (coleção, fonte, gênero) | manual |
| `tokenizer_v5_report.json` | relatório do inventário v5 do tokenizador | `scripts/build_tokenizer_v5.py` |
| `structural_proposals.tsv` | propostas para fragmentos sem `sent_id`, IDs fora de sequência e tokens trocados; aprove com `sim` na coluna `approve` | `scripts/propose_structural_fixes.py` |
| `ci-proposta/` | workflows do GitHub Actions propostos (ver abaixo) | — |

## Como usar `issues.tsv` na revisão

Categorias de **erro** que exigem decisão humana, em ordem sugerida:

1. `fragment_without_sent_id` — blocos de tokens separados da sentença anterior por uma linha em branco (em geral, continuação de citações). Decida se unem à sentença anterior ou viram sentenças próprias.
2. `token_ids_not_sequential`, `bad_token_id` — normalmente consequência do item 1.
3. `text_form_mismatch` — `# text` não corresponde aos tokens (às vezes os tokens são de outra sentença, ex.: `boe_ero_01_15`).
4. `cycle`, `root_count`, `root_mismatch`, `head_out_of_range`, `bad_head` — árvores inválidas. `root_mismatch` com `HEAD=0` e `DEPREL≠root` (320) costuma vir da anotação automática.
5. `upos_missing` — tokens sem UPOS nem XPOS.
6. `private_use_character` — caracteres de fontes legadas (U+F063, U+F086, U+F087); é preciso consultar a fonte para saber o caractere original.
7. `feat_malformed`, `deprel_not_ud`, `upos_not_ud` — rótulos restantes que não puderam ser corrigidos sem ambiguidade (`Int`, `Reflex` sem valor, `comp`, `cae`, números em DEPREL…).

Avisos (`warning`) não bloqueiam: `head_deprel_mismatch` (sintaxe parcial), `pending_tokenization` (unidade ainda sem tokens), `text_punct_mismatch` (difere só em pontuação), `feat_undocumented` (valor raro ainda sem descrição).

## Workflows propostos (`ci-proposta/`)

As ferramentas usadas nesta sessão não podem escrever em `.github/`. Para ativar:

```bash
cp CorBo/validation/ci-proposta/validate-conllu.yml .github/workflows/
cp CorBo/validation/ci-proposta/build-corbo-indexes.yml .github/workflows/   # substitui o atual
```

- `validate-conllu.yml`: roda o validador contra a linha de base, exige a camada gold sem erros e roda o `validate.py` oficial do UD (nível 2) em modo informativo.
- `build-corbo-indexes.yml`: igual ao atual, mais a geração do inventário e das camadas gold/silver.

## Propostas estruturais

```bash
python3 scripts/propose_structural_fixes.py      # gera/atualiza a planilha
# marque approve = sim nas linhas aceitas
python3 scripts/apply_structural_fixes.py        # simulação
python3 scripts/apply_structural_fixes.py --apply
python3 scripts/validate_conllu.py CorBo/Corpus_Files/CorBo.conllu --summary CorBo/validation/summary.json
cp CorBo/validation/summary.json CorBo/validation/baseline.json
```

Aprovando todas as propostas de alta e média confiança (400), os erros caem de 3.706 para 2.964: os 241 fragmentos somem, IDs fora de sequência caem de 633 para 289 e texto divergente de 1.939 para 1.853. Blocos não aprovados ficam idênticos.

## Segunda rodada: árvores, raiz e UPOS (`scripts/propose_tree_fixes.py`)

```bash
python3 scripts/propose_tree_fixes.py                 # gera tree_proposals.tsv e manual_review.tsv
python3 scripts/propose_tree_fixes.py --apply         # aplica as linhas com approve = sim
python3 scripts/propose_tree_fixes.py --apply --alta  # aplica também todas as de confiança alta
```

Tipos: `renumber_ids` (IDs repetidos → 1..n, HEADs remapeados), `set_root` (único HEAD=0 rotulado com outra relação),
`reroot` (o verbo dependente vira a raiz), `fill_upos` (forma com UPOS inequívoco no corpus; marca `Auto=upos`).
Em 22/11/2026 as 506 propostas de confiança alta foram aplicadas (erros de 1.341 para 835); registro em
`tree_applied_20261122.tsv`. As 150 de confiança média continuam em `tree_proposals.tsv` para revisão.
`manual_review.tsv` lista os erros sem correção automática (ciclos, texto ≠ tokens, traços malformados…).

### Terceira rodada e planilha texto × tokens

`propose_tree_fixes.py` também propõe `selfloop_punct` (pontuação com HEAD = ela mesma → raiz),
`selfloop_subj` (pronome sujeito com HEAD = ele mesmo → verbo seguinte; média) e `form_from_text`
(FORM difere do texto só na caixa, ou `_` onde o texto tem `-`). Aprovações já marcadas na coluna
`approve` são preservadas quando as propostas são geradas de novo.

`scripts/text_token_worksheet.py` gera `texto_tokens_revisao.tsv`: uma linha por sentença em que o
`# text` e os tokens divergem, com as diferenças no formato `[tokens]→[texto]` e as colunas `decisao`
(texto | tokens | ok) e `observacao`. Decisões já preenchidas são preservadas.
