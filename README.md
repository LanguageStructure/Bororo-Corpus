# CorBo — Corpus da Língua Bororo (v0.10.0)

> **Interface digital:** https://languagestructure.github.io/Bororo-Corpus/  
> **DOI (todas as versões, resolve para a mais recente):** https://doi.org/10.5281/zenodo.12110451  
> [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12110451.svg)](https://doi.org/10.5281/zenodo.12110451)

O **CorBo (Corpus Bororo)** é um corpus digital da língua **Boe-Bororo** (ISO 639-3: `bor`), falada em Mato Grosso, Brasil. O projeto reúne documentação textual, corpus paralelo, anotação linguística e recursos computacionais para pesquisa, documentação, ensino e desenvolvimento de tecnologia linguística.

A arquitetura atual distingue explicitamente **fonte documental**, **revisão editorial**, **anotação linguística**, **dados derivados** e **recursos experimentais de geração**. O texto das fontes é preservado; correções, normalizações e análises são registradas em camadas separadas e não substituem silenciosamente a evidência documental.

### Documentação

| Documento | Conteúdo |
|---|---|
| [Guia de anotação](docs/ANNOTATION_GUIDE.md) | convenções do CoNLL-U, decisões de anotação, marcas de anotação automática |
| [Notas da v0.10.0](docs/RELEASE_NOTES_v0.10.0.md) · [Critérios para a 1.0](docs/ROADMAP_1.0.md) | o que mudou nesta versão e o que falta para a 1.0 |
| [Ortografia e normalização](docs/ORTOGRAFIA.md) | grafia das fontes, diacríticos, caixa, pontuação, camada normalizada (rascunho) |
| [Inventário de rótulos](docs/ANNOTATION_INVENTORY.md) | UPOS, XPOS, DEPREL e FEATS em uso, com contagens (gerado automaticamente) |
| [Anotação morfológica](docs/MORPHOLOGY_ANNOTATION.md) | segmentação explícita no MISC (`Morph=`) |
| [Tokenizador](docs/TOKENIZER.md) | papel de cada arquivo do tokenizador, estados de revisão e avaliação |
| [Ética e governança](docs/ETICA_E_GOVERNANCA.md) | comunidades, parcerias, consentimento, origem dos materiais |
| [Validação](CorBo/validation/README.md) | relatórios de erros, logs de correção e decisões, proveniência das sentenças |
| [Diretrizes editoriais](CorBo_vNext/schema/EDITORIAL_GUIDELINES.md) | camadas documentais, unidades, identificadores |
| [Registro de mudanças](CHANGELOG.md) | o que mudou em cada versão |
| [Downloads](https://languagestructure.github.io/Bororo-Corpus/downloads.html) · [English](https://languagestructure.github.io/Bororo-Corpus/en.html) | arquivos para download; versão do site em inglês |
| [Pacote Python](python/README.md) | `corbo-tokenizer`: o tokenizador fora do navegador |

## Princípio documental

O fluxo editorial básico é:

```text
source witness
  → curated documentary unit
  → reviewed / parallel layer
  → linguistic annotation
  → derived indexes and interfaces
```

A fonte documental permanece primária. Uma forma revista ou normalizada não apaga a forma testemunhada. Segmentação morfológica, análise sintática e tradução são camadas adicionais e podem ter graus diferentes de completude.

### Convenção de anotação morfológica

A representação usada para evidência morfológica token-level está documentada em [`docs/MORPHOLOGY_ANNOTATION.md`](docs/MORPHOLOGY_ANNOTATION.md). O índice distingue segmentação explícita no CoNLL-U de projeções documentais por forma e não infere fronteiras morfêmicas automaticamente.


## Coleções textuais

O corpus inclui, entre outros materiais:

- **Coqueiro** — texto com alinhamento Bororo–Português;
- **História Mítica** — coleção documental e paralela;
- **Adugo Biri** — unidades com fonte, revisão e tradução;
- **Boe Ero** — 8 textos e 276 unidades paralelas, com numeração original, créditos, tradução e metadados editoriais; o arquivo de trabalho expandido integra o CoNLL-U autoritativo e o [CoNLL-U autônomo](CorBo_vNext/texts/boe-ero/boe_ero_unannotated.conllu) permanece como base documental regenerável;
- **Oiegos** — cantos Oieigo e documentos relacionados, preservados como textos independentes;
- **História da Corujinha — Tagogorogu** — narrativa de tradição oral;
- **Etnobotânica** — unidades incorporadas a partir de material tabular;
- **Textos bíblicos** — materiais bíblicos mantidos no corpus documental;
- **Bakaru Maiwu** — Novo Testamento em Bororo, tradução de Gonçalo Ochoa Camargo, SDB (Campo Grande: Missão Salesiana de Mato Grosso; FUCMT, 1992), organizado por livro, capítulo e versículo, em processo de revisão;
- **Pemo–Coqueiro** — testemunho documental colacionado contra o corpus público; 261 unidades não equivalentes são publicadas e 69 correspondências confirmadas são excluídas para evitar duplicação;
- **Archive additions** — 226 unidades documentais de fontes de arquivo auditadas contra o corpus público e incorporadas sem duplicatas fortes identificadas;
- **Archive parallel witnesses** — testemunhos paralelos colacionados unidade a unidade; 305 unidades independentes são publicadas, enquanto 55 correspondências confirmadas são mantidas apenas na camada de colação e uma unidade estruturalmente não resolvida permanece excluída.

As coleções não têm necessariamente o mesmo grau de tradução, revisão ou anotação. Ausência de uma camada não é preenchida automaticamente por inferência.

Após a integração documental de outubro de 2026, o índice público contém **10.268 unidades**. Esse total inclui **261 unidades de Pemo–Coqueiro**, **226 Archive additions** e **305 Archive parallel witnesses**. A incorporação dessas fontes usa uma camada explícita de colação: unidades `confirmed` ou `component` não são republicadas como novas unidades; `unique` e `parallel_formulaic` podem entrar no índice público; unidades `unresolved` permanecem fora até revisão humana.

## Organização dos dados

Os textos documentais em desenvolvimento encontram-se principalmente em `CorBo_vNext/` e `CorBo/Corpus_Files/`. Identificadores estáveis são usados sempre que a estrutura documental permite.

A interface pública é **somente para consulta**. A edição e revisão são feitas sobre arquivos-fonte. JSONs, índices de busca, estatísticas e outros arquivos em `docs/data/` são artefatos derivados e devem ser reconstruídos a partir das fontes, não editados como dados canônicos.

## CoNLL-U e Universal Dependencies

O componente atualmente usado para anotação morfossintática e visualização de dependências tem como arquivo autoritativo:

```text
CorBo/Corpus_Files/CorBo.conllu
```

Este é o arquivo canônico unificado usado para anotação continuada, construção do índice UD atual, análise de formas e recursos morfológicos derivados associados ao gerador. Ele consolida as fontes CoNLL-U anteriormente mantidas separadamente, preservando a proveniência por meio de comentários `# source_conllu`, quando disponível.

Arquivos CoNLL-U legados, incluindo versões enriquecidas com material bíblico como `Bororo_UD_enriched_v5_plus_scripture.conllu`, **não são a fonte do visualizador UD atual**. Textos bíblicos podem permanecer no corpus documental e em outros índices, mas não são projetados automaticamente no visualizador de dependências.

O visualizador apresenta apenas sentenças efetivamente presentes no CoNLL-U autoritativo. As árvores representam **HEAD → DEPENDENTE** e não são completadas por sintaxe inferida ou gerada.

### Metadados e proveniência

Os comentários CoNLL-U podem registrar, quando disponíveis:

- `sent_id`;
- `text`;
- `text_por`;
- `text_eng`.
- `auto_annotation`, `auto_fields`, `auto_tokens`, `auto_note` — sentença com campos preenchidos automaticamente e ainda pendentes de revisão manual (no nível do token, `Auto=` no MISC indica quais campos);
- `source_unit`, `section` — unidade e seção da fonte documental (Boe Ero);
- `model_projection` — origem de uma projeção automática a partir de sentença gold.

As convenções completas estão no [guia de anotação](docs/ANNOTATION_GUIDE.md).

O CoNLL-U unificado preserva a origem dos componentes anteriores por meio de comentários `# source_conllu`. Metadados documentais mais específicos ainda não estão disponíveis de maneira uniforme para todas as sentenças, de modo que alguns splits históricos por fonte podem não ser reconstruíveis apenas a partir do arquivo público atual.

Para novas incorporações e revisões, o objetivo é preservar também, quando conhecido:

- `source` / `document_id`;
- `source_unit_id`;
- coleção ou testemunho documental;
- relação entre a unidade documental e a sentença anotada.

Isso permitirá futuros splits por fonte plenamente reproduzíveis sem inferir proveniência a partir do conteúdo.

## Validação e camadas gold / silver

O CoNLL-U canônico é verificado por `scripts/validate_conllu.py` (estrutura, rótulos UD, inventário de traços, coerência `# text` × formas). O relatório completo, com número de linha e `sent_id`, fica em `CorBo/validation/issues.tsv`; as contagens em `CorBo/validation/summary.json`. Correções automáticas sem ambiguidade linguística são feitas por `scripts/fix_conllu_safe.py`, que registra cada alteração em `CorBo/validation/safe_fixes.tsv`. Problemas que exigem decisão humana (ciclos, raízes múltiplas, texto divergente das formas, fragmentos sem `sent_id`) não são corrigidos automaticamente.

`scripts/split_gold_silver.py` deriva, sem alterar o arquivo canônico:

- `CorBo/Corpus_Files/splits/CorBo.gold.conllu` — anotação inteiramente manual, sintaxe completa e sem erros estruturais;
- `CorBo/Corpus_Files/splits/CorBo.silver.conllu` — estruturalmente válida, com anotação automática (`Auto=`);
- `CorBo/Corpus_Files/splits/review_sentences.tsv` — sentenças a revisar;
- `docs/data/annotation-coverage.json` — números exibidos na página **Cobertura** do site.

Estado na v0.10.0 (22 de novembro de 2026): 12.020 unidades no CoNLL-U, das quais 11.760 tokenizadas (79.521 tokens); **1.900 sentenças gold** (9.802 tokens), **8.980 silver** e 880 a revisar; 260 unidades aguardam tokenização; 706 erros de validação restantes. Cerca de 70% dos tokens têm ao menos um campo preenchido automaticamente (`Auto=`, `AutoLowConf=` ou `PosMorphAnnot=AI:…`).

Para impedir regressões, a linha de base `CorBo/validation/baseline.json` registra o número de erros por categoria; a validação em CI falha se alguma categoria aumentar. Ao corrigir erros, atualize-a com `cp CorBo/validation/summary.json CorBo/validation/baseline.json`.

O inventário de UPOS, XPOS, DEPREL e FEATS efetivamente usados é gerado por `scripts/build_annotation_inventory.py` em [`docs/ANNOTATION_INVENTORY.md`](docs/ANNOTATION_INVENTORY.md).

## Anotação morfológica

A análise morfológica é mantida separada da transcrição documental. Uma segmentação não deve ser inferida apenas pela grafia.

Os recursos derivados distinguem:

- forma;
- lema;
- UPOS/XPOS;
- FEATS explicitamente anotados;
- morfemas explicitamente analisados;
- relações de dependência.

A busca por morfema usa segmentação/anotação explícita, não correspondência arbitrária de substring. A segmentação está no MISC como `Morph=` (12.478 tokens; `-` marca fronteira afixal, `=` clítica e `0` o morfema zero); o build lê `Morph=` e `MORPH=` como equivalentes. A página **Análise de formas** também se baseia em anotações explícitas.

## Interface digital

A interface pública está em:

**https://languagestructure.github.io/Bororo-Corpus/**

Ela inclui:

- catálogo e leitores de textos;
- busca de palavras em contexto;
- busca morfológica;
- análise de formas;
- visualizador CoNLL-U/UD;
- estatísticas;
- ferramentas experimentais de geração controlada.

Nos leitores em que essa integração está disponível, formas Bororo são clicáveis e levam à exploração lexical/corpus correspondente.

## Gerador controlado

O CorBo mantém uma camada experimental de geração baseada exclusivamente em análises licenciadas. O princípio é:

```text
corpus evidence
  → human linguistic analysis
  → explicit license
  → deterministic realization
```

**Atestação não é licença.** Uma forma observada no corpus não se torna automaticamente uma regra produtiva. Da mesma forma, uma combinação não observada não é declarada agramatical apenas por ausência.

Os inventários públicos incluem, entre outros:

- `docs/data/generator-frames.json`;
- `docs/data/generator-attested-forms.json`;
- `docs/data/generator-morphology-rules.json`;
- `docs/data/generator-intent-schema.json`.

O gerador usa correspondência exata com combinações licenciadas e deve falhar de modo controlado quando uma combinação, frame ou predicado não está representado.

## Interface de linguagem natural

A camada experimental de intent segue a arquitetura:

```text
Portuguese / English
  → AI semantic/grammatical interpretation
  → language-neutral structured intent
  → deterministic CorBo validator
  → controlled Bororo realization
```

A IA **não gera livremente Bororo**, não cria morfologia, não inventa predicados Bororo e não concede licenças. A realização linguística pertence à camada determinística.

O serviço está em `services/intent/`, e o contrato público da intenção estruturada está em `docs/data/generator-intent-schema.json`.

### Challenge set congelado

A interface foi testada em um challenge set congelado de **30 casos**:

- 15 positivos;
- 5 ambíguos;
- 10 boundary cases.

Na primeira execução completa registrada:

- 30/30 decisões do validador corresponderam ao gold;
- 20/20 intents com gold explícito corresponderam ao esperado;
- 16/16 realizações de sujeito com gold explícito corresponderam ao esperado;
- 5/5 casos ambíguos foram enviados para clarificação;
- 10/10 boundary cases receberam a decisão esperada;
- 0 falhas de transporte.

Esse resultado é **agreement no challenge set controlado**, não uma estimativa de accuracy geral para linguagem natural ou geração irrestrita em Bororo.

A metodologia e o snapshot do primeiro run completo estão documentados em:

- `services/intent/EVALUATION.md`;
- `services/intent/evaluation.json`;
- `services/intent/evaluation-run-2026-10-03.json`.

## Relação com o Bororo Sentence Generator

A implementação experimental e a avaliação formal do gerador são também distribuídas separadamente no repositório:

**LanguageStructure/Bororo-Sentence-Generator-**

O CorBo é a fonte documental e anotada; o Sentence Generator é um artefato experimental que consome análises revisadas. Os dois projetos não devem ser confundidos: alterações na documentação do corpus não atualizam automaticamente a gramática do gerador.

O repositório do gerador contém manifests de avaliação, challenge sets, testes e o protocolo formal de adjudicação humana.

## Princípios editoriais e de governança

O CorBo adota os seguintes princípios:

- preservar a forma presente na fonte;
- registrar revisão/normalização em camada separada;
- não corrigir silenciosamente irregularidades documentais;
- permitir unidades sem tradução ou análise completa;
- não projetar automaticamente segmentação ou sintaxe sobre a fonte;
- tratar índices e estatísticas como dados derivados;
- distinguir atestação, análise e licença de geração;
- registrar incerteza em vez de completá-la por analogia;
- preservar proveniência documental sempre que disponível.

## Formatos

Os principais formatos são:

- **CoNLL-U** — anotação morfossintática e dependências;
- **TSV/CSV** — textos paralelos, camadas editoriais e dados tabulares;
- **JSON** — índices e recursos derivados;
- **TXT** — fontes documentais em texto simples.

## Estado da versão

A versão 0.10.0 (publicada no Zenodo em 22 de novembro de 2026) é uma **versão de pesquisa em desenvolvimento**. Parte das traduções em português está desalinhada e em revisão manual; a camada silver é anotação automática. Os critérios para a versão 1.0 estão em [`docs/ROADMAP_1.0.md`](docs/ROADMAP_1.0.md). Coleções e camadas encontram-se em estágios distintos de revisão documental, ortográfica, tradutória e linguística. Algumas análises permanecem deliberadamente incompletas ou sob revisão.

A infraestrutura atual privilegia a rastreabilidade dessas diferenças em vez de produzir artificialmente um corpus inteiramente normalizado.

## Língua e região

- **Língua:** Boe-Bororo
- **ISO 639-3:** `bor`
- **Família:** Bororoan
- **Região:** Mato Grosso, Brasil

## Novidades da v0.10.0 (novembro de 2026)

- **Validação do CoNLL-U** com relatório por linha e linha de base em CI (`.github/workflows/validate-conllu.yml`); 7.179 correções automáticas sem ambiguidade (erros de 4.893 para 3.706).
- **Camadas gold e silver** derivadas do arquivo canônico e painel correspondente na página Cobertura.
- **Decisões de anotação** (21/11/2026): `Boe` = "os Bororo" → PROPN plural, demais acepções → NOUN singular; sufixo *-go* = `Voice=CauInc`; `Aspect=IncProg`; `Number=Sgtv` = singulativo; `dukeje` = SCONJ (`mark`) ou ADV (`advmod`); complementos oracionais de `ako` = `ccomp`, orações citadas independentes = `parataxis`. Registro em `CorBo/validation/decisions_20261121.tsv`.
- **Busca por morfema** passa a usar as segmentações `Morph=` do CoNLL-U (de 29 para 28.604 ocorrências).
- **Tokenizador v5**: pré-tokenização, estado de revisão explícito, suporte baixo, superfície × subjacente e suspeita de português/empréstimo; planilha de 400 formas para o gold de avaliação.
- **Documentação**: guia de anotação, inventário de rótulos, ética e governança, proveniência dos grupos de sentenças (`CorBo/validation/sent_id_groups.tsv`).
- **Site**: painel lexical único, cabeçalho comum, versão em inglês, página de downloads, link permanente e "sugerir correção" por unidade, árvores UD exportáveis em SVG (e corrigidas: nenhuma árvore aparecia), estatísticas pré-calculadas, schema.org/sitemap/OLAC.
- Pendências: valores raros de `Mood`, `Number=Col` e `Voice=CPass`; proveniência das sentenças de ID numérico e `dic_`.

## Novidades da versão 0.8.0

A versão 0.8.0 consolida a expansão documental e editorial realizada após 0.7.1.

- índice público ampliado para **10.268 unidades**, **242.229 tokens** e **17.026 formas gráficas distintas**;
- integração de **261 unidades Pemo–Coqueiro** após colação documental;
- integração de **226 Archive additions** após auditoria contra o corpus público;
- integração de **305 Archive parallel witnesses** adjudicados como `unique` ou `parallel_formulaic`;
- exclusão de correspondências `confirmed` para impedir contagem duplicada de testemunhos;
- manutenção de `CIR.001` fora do índice público enquanto a estrutura da fonte permanecer `unresolved`;
- ampliação da busca por formas, lemas e morfemas;
- camada CoNLL-U com **973 sentenças** e **3.765 tokens** naquela versão, das quais **874** possuíam análise de dependência com raiz sintática explicitamente anotada (os números atuais estão na seção *Validação e camadas gold / silver*);
- visualização UD restrita às sentenças efetivamente anotadas no CoNLL-U autoritativo;
- melhorias no editor, na busca por morfemas, no visualizador UD e nas páginas de exploração do corpus;
- atualização do guia **Como usar**, estatísticas, manifesto de fontes e documentação da metodologia de colação.

### Expansão documental e colação

O foco desta versão é a **expansão documental, incorporação de testemunhos arquivísticos e colação textual**. A incorporação foi feita de modo conservador: correspondências documentais já representadas no corpus foram marcadas como `confirmed` e excluídas da contagem de novas unidades; paralelos formulares sem equivalência textual estrita permanecem identificados como `parallel_formulaic`.

Entre os conjuntos incorporados e colacionados estão **Pemo–Coqueiro, Aijedoge, Barujauwo, Primeiras Andanças, Gêmeos Bakororodoge, Aroeceba, Arua Bororo, Arua Bororo II, Bakororodoge, Façanha Bakororogode, Ipare Ewororo, Jakomea Jiwu** e **Cirilo Discurso**.

## Tokenizador experimental baseado no CoNLL-U

A interface pública de [tokenização](docs/tokenizer.html) oferece dois modos: separação ortográfica e segmentação linguística experimental. As unidades identificadas podem ser selecionadas para consultar informações lexicais e, quando disponíveis, a justificativa de uma segmentação proposta.

O treinamento reproduzível é realizado por `scripts/train_tokenizer.py`, usando as colunas `FORM`, `LEMMA` e `UPOS` do arquivo canônico `CorBo/Corpus_Files/CorBo.conllu`. O resultado é publicado em `docs/data/tokenizer-model.json`; o fluxo `.github/workflows/tokenizer-model.yml` reconstrói o modelo quando o arquivo CoNLL-U ou o programa de treinamento muda.

```bash
python3 scripts/train_tokenizer.py
```

O modelo reúne frequências de formas, famílias de lemas, correspondências entre formas e lemas, padrões recorrentes em famílias lexicais distintas e **segmentações candidatas**. A classificação da evidência distribucional distingue padrões de suporte baixo (pelo menos três lemas), médio (cinco lemas e 20 ocorrências) e alto (dez lemas e 50 ocorrências). A classificação de uma segmentação considera a fronteira menos sustentada; fronteiras sem suporte independente impedem a atribuição de grau. **Essas categorias não constituem validação linguística nem medem precisão preditiva.**

O tokenizador mantém análises linguísticas cadastradas separadas das hipóteses geradas automaticamente. Entre os exemplos explicitamente cadastrados estão `ure → u + re` e `nure → nu + re`. A aprendizagem estatística não autoriza tratar terminações frequentes como morfemas: `-je` é excluído da inferência de sufixos e `-dure` exige cautela, pois pode atravessar fronteiras morfológicas. Formas lexicais não devem ser divididas apenas por coincidência gráfica, como uma terminação `-re`.

**Estado de desenvolvimento (outubro de 2026).** O último modelo público verificado continha 74.255 ocorrências, 6.674 formas distintas, 236 famílias de lemas, 27 padrões entre famílias e 83 propostas de segmentação. Esses números descrevem o artefato verificado, não necessariamente o resultado do próximo treinamento. O código para atribuir graus de evidência já foi atualizado, mas a publicação de um JSON regenerado com esses campos ainda precisa ser confirmada. A avaliação com dados separados do treinamento e revisão linguística das propostas continuam pendentes.

### Inventário v5 do tokenizador

`scripts/build_tokenizer_v5.py` gera `docs/data/tokenizer-v5-site.json`, usado pela página do tokenizador (com recuo automático para o v4). Ele não altera análises; acrescenta pré-tokenização (pontuação, números e citações de afixos deixam de ser formas lexicais), suspeita de português ou empréstimo (`lang_suspect`, com a evidência gráfica), estado de revisão explícito (`confirmed`, `proposed`, `proposed_low_support`, `unanalysed`), suporte da família lexical e a distinção entre `surface_segments` (fatias da grafia) e `underlying_morphemes` (representação morfológica, p. ex. `amode → a + modu + re`). O relatório fica em `CorBo/validation/tokenizer_v5_report.json`. O papel de cada arquivo do tokenizador está em [`docs/TOKENIZER.md`](docs/TOKENIZER.md).

Para a avaliação independente, `scripts/prepare_tokenizer_gold_worksheet.py` gerou `CorBo_vNext/annotations/tokenizer_gold_worksheet_v1.tsv`: 400 formas estratificadas por frequência e estado, com divisão train/test fixa e um exemplo do corpus para cada uma, **sem** mostrar a análise do modelo. Depois de anotada, ela é lida diretamente por `scripts/evaluate_tokenizer_gold.py --gold …` (linhas ainda vazias são ignoradas).

## Ética e governança dos dados

Consentimento, papel da comunidade Boe, direitos sobre os materiais e restrições de acesso estão em [`docs/ETICA_E_GOVERNANCA.md`](docs/ETICA_E_GOVERNANCA.md).

## Licença e citação

O corpus é disponibilizado sob **CC BY 4.0** (Atribuição).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12110451.svg)](https://doi.org/10.5281/zenodo.12110451)

DOI de todas as versões: [10.5281/zenodo.12110451](https://doi.org/10.5281/zenodo.12110451). Esta versão (v0.10.0): [10.5281/zenodo.24441715](https://doi.org/10.5281/zenodo.24441715). Versões anteriores: v0.9.0 [10.5281/zenodo.23441622](https://doi.org/10.5281/zenodo.23441622), v0.8.0 [10.5281/zenodo.23187959](https://doi.org/10.5281/zenodo.23187959). Até a v0.9.0 o registro do Zenodo indicava CC BY 4.0, enquanto este README indicava CC BY-NC-SA 4.0; a partir da v0.10.0 a licença é CC BY 4.0 em todos os lugares.
Ao utilizar o corpus, cite a versão específica consultada no Zenodo. As versões arquivadas fornecem registros estáveis; o repositório e a interface pública podem continuar recebendo atualizações.

## Autoria, parcerias e comunidades

- **Fabrício Ferraz Gerardi** — organização, trabalho de campo (`FFG-FW`), revisão editorial, anotação manual e correções do CoNLL-U.
- **Parceiros:** Mariel Kujibo Ekureu, Fernando Kudoro e a Missão Salesiana. Os autores do Boe Ero (*Vida Bororo*) e de outros materiais do corpus são missionários salesianos que viveram em Meruri.
- **Comunidades:** Aldeia Meruri (TI Meruri), Tadarimana e Córrego Grande.
- Narrativas de Jussila, coletadas por Fabrício Ferraz Gerardi.

O CorBo é desenvolvido no âmbito da iniciativa **Boe eno moto**, dedicada à documentação, pesquisa, ensino e revitalização da língua Bororo.
