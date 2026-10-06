# CorBo — Corpus da Língua Bororo (v0.7.1)

> **Interface digital:** https://languagestructure.github.io/Bororo-Corpus/  
> **DOI:** https://doi.org/10.5281/zenodo.22976962

O **CorBo (Corpus Bororo)** é um corpus digital da língua **Boe-Bororo** (ISO 639-3: `bor`), falada em Mato Grosso, Brasil. O projeto reúne documentação textual, corpus paralelo, anotação linguística e recursos computacionais para pesquisa, documentação, ensino e desenvolvimento de tecnologia linguística.

A arquitetura atual distingue explicitamente **fonte documental**, **revisão editorial**, **anotação linguística**, **dados derivados** e **recursos experimentais de geração**. O texto das fontes é preservado; correções, normalizações e análises são registradas em camadas separadas e não substituem silenciosamente a evidência documental.

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

## Coleções textuais

O corpus inclui, entre outros materiais:

- **Coqueiro** — texto com alinhamento Bororo–Português;
- **História Mítica** — coleção documental e paralela;
- **Adugo Biri** — unidades com fonte, revisão e tradução;
- **Boe Ero** — coleção documental com seções, numeração original, tradução e metadados editoriais;
- **Oiegos** — cantos Oieigo e documentos relacionados, preservados como textos independentes;
- **História da Corujinha — Tagogorogu** — narrativa de tradição oral;
- **Etnobotânica** — unidades incorporadas a partir de material tabular;
- **Textos bíblicos** — materiais bíblicos mantidos no corpus documental;
- **Bakaru Maiwu** — Novo Testamento em Bororo, organizado por livro, capítulo e versículo, em processo de revisão;
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
CorBo/Corpus_Files/exemplosDicBor_full_review_pass17_incomplete_first.conllu
```

Este é o arquivo usado para construir o índice UD atual, a análise de formas e os recursos morfológicos derivados associados ao gerador.

Arquivos CoNLL-U legados, incluindo versões enriquecidas com material bíblico como `Bororo_UD_enriched_v5_plus_scripture.conllu`, **não são a fonte do visualizador UD atual**. Textos bíblicos podem permanecer no corpus documental e em outros índices, mas não são projetados automaticamente no visualizador de dependências.

O visualizador apresenta apenas sentenças efetivamente presentes no CoNLL-U autoritativo. As árvores representam **HEAD → DEPENDENTE** e não são completadas por sintaxe inferida ou gerada.

### Metadados e proveniência

Os comentários CoNLL-U podem registrar, quando disponíveis:

- `sent_id`;
- `text`;
- `text_por`;
- `text_eng`.

O CoNLL-U atual ainda não preserva de maneira uniforme o grupo documental original de cada sentença. Essa limitação impede, em alguns experimentos históricos, a reconstrução exata de antigos splits por fonte apenas a partir do arquivo público atual.

Para novas incorporações e revisões, o objetivo é preservar também, quando conhecido:

- `source` / `document_id`;
- `source_unit_id`;
- coleção ou testemunho documental;
- relação entre a unidade documental e a sentença anotada.

Isso permitirá futuros splits por fonte plenamente reproduzíveis sem inferir proveniência a partir do conteúdo.

## Anotação morfológica

A análise morfológica é mantida separada da transcrição documental. Uma segmentação não deve ser inferida apenas pela grafia.

Os recursos derivados distinguem:

- forma;
- lema;
- UPOS/XPOS;
- FEATS explicitamente anotados;
- morfemas explicitamente analisados;
- relações de dependência.

A busca por morfema usa segmentação/anotação explícita, não correspondência arbitrária de substring. A página **Análise de formas** também se baseia em anotações explícitas.

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

A versão 0.7.1 é uma **versão de pesquisa em desenvolvimento**. Coleções e camadas encontram-se em estágios distintos de revisão documental, ortográfica, tradutória e linguística. Algumas análises permanecem deliberadamente incompletas ou sob revisão.

A infraestrutura atual privilegia a rastreabilidade dessas diferenças em vez de produzir artificialmente um corpus inteiramente normalizado.

## Língua e região

- **Língua:** Boe-Bororo
- **ISO 639-3:** `bor`
- **Família:** Bororoan
- **Região:** Mato Grosso, Brasil

## Novidades da versão 0.8.0

A versão 0.8.0 consolida a expansão documental e editorial realizada após 0.7.1.

- índice público ampliado para **10.268 unidades**, **242.229 tokens** e **17.026 formas gráficas distintas**;
- integração de **261 unidades Pemo–Coqueiro** após colação documental;
- integração de **226 Archive additions** após auditoria contra o corpus público;
- integração de **305 Archive parallel witnesses** adjudicados como `unique` ou `parallel_formulaic`;
- exclusão de correspondências `confirmed` para impedir contagem duplicada de testemunhos;
- manutenção de `CIR.001` fora do índice público enquanto a estrutura da fonte permanecer `unresolved`;
- ampliação da busca por formas, lemas e morfemas;
- visualização UD restrita às sentenças efetivamente anotadas no CoNLL-U autoritativo;
- atualização do guia **Como usar**, estatísticas, manifesto de fontes e documentação da metodologia de colação.

## Licença e citação

O corpus é disponibilizado sob **CC BY-NC-SA 4.0** (Atribuição–NãoComercial–CompartilhaIgual).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22976962.svg)](https://doi.org/10.5281/zenodo.22976962)

Ao utilizar o corpus, cite a versão específica consultada no Zenodo. As versões arquivadas fornecem registros estáveis; o repositório e a interface pública podem continuar recebendo atualizações.

## Autor

- **Fabrício Ferraz Gerardi**

O CorBo é desenvolvido no âmbito da iniciativa **Boe eno moto**, dedicada à documentação, pesquisa, ensino e revitalização da língua Bororo.
