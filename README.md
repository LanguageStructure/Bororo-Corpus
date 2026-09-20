# Bororo-Corpus (CorBo) (Pré-lançamento v0.7)

> **Interface digital do corpus:** https://languagestructure.github.io/Bororo-Corpus/

O **CorBo (Corpus Bororo)** é um corpus digital da língua **Boe-Bororo** (ISO 639-3: `bor`), língua do tronco Macro-Jê falada no estado de Mato Grosso, Brasil. O corpus foi concebido como uma infraestrutura aberta de pesquisa voltada à documentação linguística, linguística de corpus, descrição e análise gramatical, processamento de linguagem natural e desenvolvimento de recursos educacionais e de revitalização linguística.

A versão **0.7** amplia o componente textual do CorBo e consolida uma arquitetura que distingue os **dados documentais de origem**, a **revisão editorial**, a **anotação linguística** e os **recursos derivados automaticamente**. A grafia e o conteúdo dos documentos-fonte são preservados, enquanto formas revisadas podem ser mantidas em uma camada editorial separada.

O corpus reúne diferentes coleções textuais, entre elas **Coqueiro**, **História Mítica**, **Adugo Biri**, **Boe Ero**, textos bíblicos e o **Bakaru Maiwu**, o Novo Testamento em Bororo. Quando disponíveis, os textos em Bororo são alinhados a traduções em português e, em partes do corpus, em inglês.

O componente linguisticamente anotado segue o modelo **Universal Dependencies (UD)** e é disponibilizado em formato CoNLL-U. O CorBo é desenvolvido no âmbito da iniciativa **Boe eno moto**, dedicada à documentação, pesquisa, ensino e revitalização da língua Bororo.

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

## 📊 Estatísticas

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

[![DOI](https://zenodo.org/badge/772146862.svg)](https://doi.org/10.5281/zenodo.12110451)

---

## 🔜 Próximos passos

- ✅ Completar os campos faltantes (`GLOSS`, `CLS`, `PRCLITIC`)  
- ✅ Revisar e traduzir as sentenças para o inglês  
- ✅ Adicionar segmentação morfológica (`GLOSS_SEG`)  
- ✅ Incluir metadados de falantes e gravações de áudio  
- ✅ Publicar versão estável com DOI no [Zenodo](https://zenodo.org/)

---

*Preparado por **Fabrício Marcel Ferraz Gerardi**  
(Boe eno moto — Projeto de Língua Bororo, Universidade de Tübingen)*
