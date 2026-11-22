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
