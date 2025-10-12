# Bororo-Corpus (CorBo) (Pré-lançamento v0.5)

Este corpus contém dados da **língua Boe-Bororo**, anotados segundo o padrão
[Universal Dependencies](https://universaldependencies.org/).
Integra traduções alinhadas, glossas lexicais e metadados provenientes
de diversas fontes do projeto **Boe eno moto**.

---

## 📦 Conteúdo do pacote

| Arquivo | Descrição |
|----------|------------|
| **Bororo_UD_enriched_v5.conllu** | Corpus principal com anotações UD, traduções (PT/EN), enriquecimento lexical e metadados por sentença. |
| **Bororo_UD_enriched_v5_meta_report.txt** | Relatório com estatísticas de alinhamento e metadados. |
| **bororo_lexical_summary.tsv** | Sumário lexical com frequência dos lemas, glossas, classificadores (CLS) e proclíticos. |
| **bororo_lexical_missing_fields.tsv** | Lista dos lemas que ainda não possuem glossas, CLS ou proclíticos preenchidos. |
| **bororo_corpus_parallel.csv** | Corpus paralelo (Bororo ↔ Português) usado para o alinhamento das traduções. |
| **bororo_lexicon_template_for_enrichment.csv** | Léxico utilizado para enriquecer os campos MISC (GLOSS, CLS, PRCLITIC). |
| **README.md** | Este documento. |

---

## 🧩 Estrutura do arquivo CoNLL-U

Cada linha de token segue o formato padrão UD (10 colunas):

**Comentários por sentença:**

text = <sentença em Bororo>

translation_pt = <tradução em português>

translation_en = <tradução em inglês (provisória)>

meta: sourcefile=; genre=<ritual|narrative|unknown>;

elicitation=no; align_tier=<exact|basic|strong|noacc|punctless|none>

**Campos do MISC:**

| Campo | Descrição |
|--------|------------|
| `LEMMA_SRC` | Origem do lema (`conllu` ou dicionário) |
| `POS_FINE` | Classe gramatical detalhada (derivada de XPOS ou UPOS) |
| `ORTHO` | Forma ortográfica |
| `GLOSS` | Glossa lexical (manual ou do dicionário) |
| `CLS` | Classe de posse / classificador (`o`, `ke`, `aku`, `imo`, `kuie`, `kudawu` etc.) |
| `PRCLITIC` | Proclítico (ex.: `i=`, `a=`, `bo=`, `ka=`) |
| `GLOSS_SEG` | Glossa segmentada (a ser adicionada nas próximas versões) |
| `AUDIO` | Caminho para o áudio do token (previsto para a versão futura) |

---

## 🌍 Fontes de dados

| Fonte | Tipo | Observações |
|--------|------|-------------|
| `Aroe Etawujedu.txt` | Texto ritual (canto tradicional) | Classificado como gênero `ritual` |
| `pedrosa_monolingue.csv` | Texto monolíngue de Pedrosa | Classificado como gênero `narrative` |
| `bororo_corpus_parallel.csv` | Corpus paralelo (Bororo ↔ Português) | Fornece as traduções e metadados de origem |
| `bororo_nt_clean.csv`, `monolingual.csv` | Material monolíngue complementar | Usado para validação lexical |

---

## 🧠 Convenções de anotação

- **Língua:** Boe-Bororo (ISO 639-3: `bor`)
- **Sistema de escrita:** Alfabeto latino (ortografia modernizada)
- **Segmentação de sentenças:** baseada nos textos-fonte e no corpus paralelo.
- **Morfologia:** atualmente limitada ao nível de palavra (lemas e glossas);
  a segmentação morfológica (`GLOSS_SEG`) será incluída em próxima versão.
- **Traduções:** `translation_pt` revisada; `translation_en` é cópia provisória do português.
- **Metadados:** inferidos a partir do campo `sourcefile` e de heurísticas de gênero.

---

## 📊 Estatísticas (pré-lançamento v5)

Ver `Bororo_UD_enriched_v5_meta_report.txt` para detalhes.

| Métrica | Valor aproximado |
|----------|------------------|
| Sentenças totais | ≈ [ver relatório] |
| Tokens | ≈ [ver relatório] |
| Com tradução alinhada (PT) | ~90–95% |
| Com glossa lexical (`GLOSS`) | ~[valor]% |
| Com classificador (`CLS`) | ~[valor]% |
| Com proclítico (`PRCLITIC`) | ~[valor]% |

---

## 🧮 Níveis de alinhamento

| Nível | Descrição |
|--------|------------|
| `exact` | Correspondência exata com o corpus paralelo. |
| `basic` | Após remoção de espaços extras. |
| `strong` | Normalização de maiúsculas/minúsculas e pontuação. |
| `noacc` | Após remoção de acentos. |
| `punctless` | Após remoção total de pontuação. |
| `none` | Nenhum alinhamento encontrado (sem tradução). |

---

## 🏷️ Licença e citação

O corpus é disponibilizado para uso **acadêmico e educacional**, sob a licença  
**CC-BY-NC-SA 4.0** (Atribuição–NãoComercial–CompartilhaIgual).

**Citação recomendada:**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17334055.svg)](https://doi.org/10.5281/zenodo.17334055)


---

## 🔜 Próximos passos (para a versão completa)

- ✅ Completar os campos faltantes (`GLOSS`, `CLS`, `PRCLITIC`)  
- ✅ Revisar e traduzir as sentenças para o inglês  
- ✅ Adicionar segmentação morfológica (`GLOSS_SEG`)  
- ✅ Incluir metadados de falantes e gravações de áudio  
- ✅ Publicar versão estável com DOI no [Zenodo](https://zenodo.org/)

---

*Preparado por **Fabrício Marcel Ferraz Gerardi**  
(Boe eno moto — Projeto de Língua Bororo, Universidade de Tübingen)*
