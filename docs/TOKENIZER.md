# Arquivos do tokenizador

Mapa dos arquivos, de onde vêm e quem os usa. Os JSONs em `docs/data/` são **derivados**: corrija as fontes e reconstrua.

| Arquivo | Gerado por | Usado por | Papel |
|---|---|---|---|
| `docs/data/tokenizer-model.json` | `scripts/train_tokenizer.py` (CI: `tokenizer-model.yml`) | `tokenizer.html` | modelo distribucional treinado no CoNLL-U (famílias de lemas, padrões, candidatas) |
| `docs/data/tokenizer-v2.json` | `scripts/build_tokenizer_v2.py` | `tokenizer.html`, `forms.html`, `word.html` | análises conservadoras por forma (`confirmed` / `proposed` / `unanalysed`) e `support` |
| `docs/data/tokenizer-lexicon-v3.json` | revisão manual | v4, v5 | inventário lexical externo com `surface_segments` e `underlying_morphemes` |
| `docs/data/tokenizer-v3.json` | `scripts/integrar_tokenizador_v3.py` | v4 | v2 + `CorBo_vNext/annotations/tokenizer_confirmed_inventory.tsv` |
| `docs/data/tokenizer-v4.json`, `tokenizer-v4-site.json` | integração de 2026-11-18 (sem script no repositório) | v5; recuo do site | v3 + confirmações e `-guraga` |
| **`docs/data/tokenizer-v5-site.json`** | **`scripts/build_tokenizer_v5.py`** | **`tokenizer.html`** (com recuo para o v4) | **inventário único do site**: v4 + pré-tokenização, `review_status`, suporte, superfície × subjacente, suspeita de português |

Relatório do v5: `CorBo/validation/tokenizer_v5_report.json` (formas suspeitas de português, confirmadas não concatenativas, pontuação removida das bordas, caracteres de uso privado).

## Estados de revisão (v5)

| `review_status` | Significado |
|---|---|
| `confirmed` | segmentação confirmada por revisão humana |
| `proposed` | hipótese do modelo, com família lexical de pelo menos 3 ocorrências |
| `proposed_low_support` | hipótese com menos de 3 ocorrências na família; exibida com aviso |
| `unanalysed` | forma reconhecida, sem segmentação registrada |

`lang_suspect: "pt"` é só um indício gráfico (diacríticos; dígrafos *lh, nh, qu, ss, rr*) e inclui empréstimos com morfologia Bororo (*caminhãoto*, *açucarogu*). Não exclui a forma e não é classificação.

## Superfície e subjacente

Algumas análises confirmadas não reconstroem a grafia: `amode → a + modu + re`, `inago → i(n) + ago`. No v5, `underlying_morphemes` guarda a análise e `surface_segments` guarda as fatias da grafia quando são conhecidas (`null` quando não). **Pendente:** registrar as fatias de superfície dessas 10 formas no `tokenizer-lexicon-v3.json`.

## Avaliação

1. Anote `CorBo_vNext/annotations/tokenizer_gold_worksheet_v1.tsv` (gerada por `scripts/prepare_tokenizer_gold_worksheet.py`): preencha `surface_segments` (ex.: `a+ka+re`) e `decision` (`confirmed`, `ambiguous`, `unresolved`, `reject`). A planilha não mostra a análise do modelo.
2. `python3 scripts/evaluate_tokenizer_gold.py --gold CorBo_vNext/annotations/tokenizer_gold_worksheet_v1.tsv --report …` (só o split `test` é pontuado; linhas vazias são ignoradas).
3. Siga [`tokenizer-evaluation-protocol.md`](tokenizer-evaluation-protocol.md) para o congelamento e a revisão cega.
