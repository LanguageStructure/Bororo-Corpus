# CorBo — Corpus da Língua Bororo (v0.7)

> **Interface digital:** https://languagestructure.github.io/Bororo-Corpus/  
> **DOI:** https://doi.org/10.5281/zenodo.12110451

O **CorBo (Corpus Bororo)** é um corpus digital da língua **Boe-Bororo** (ISO 639-3: `bor`), língua do tronco Macro-Jê falada em Mato Grosso, Brasil. O projeto reúne documentação textual, corpus paralelo, anotação linguística e recursos computacionais em uma infraestrutura destinada à pesquisa, à documentação linguística, ao processamento de linguagem natural e ao desenvolvimento de materiais para ensino e revitalização da língua.

A versão **0.7** amplia substancialmente o componente textual e consolida uma arquitetura que distingue **fonte documental**, **revisão editorial**, **anotação linguística** e **dados derivados**. O texto das fontes é preservado; correções e formas revistas são registradas em camada separada, evitando que decisões editoriais substituam silenciosamente a evidência documental.

## Coleções textuais

O corpus inclui atualmente:

- **Coqueiro** — texto com alinhamento Bororo–Português;
- **História Mítica** — coleção documental e paralela;
- **Adugo Biri** — texto organizado em unidades estáveis, com fonte, revisão e tradução;
- **Boe Ero** — coleção documental com seções, numeração original, tradução e metadados editoriais;
- **Textos bíblicos** — materiais bíblicos incorporados ao corpus;
- **Bakaru Maiwu** — Novo Testamento em Bororo, organizado por livro, capítulo e versículo, atualmente em processo de revisão.

As coleções não apresentam necessariamente o mesmo grau de tradução ou anotação. Quando disponíveis, traduções em português e inglês são mantidas junto às unidades correspondentes.

## Organização dos dados

A estrutura atual separa os dados primários dos recursos gerados automaticamente. Os textos em desenvolvimento encontram-se principalmente em `CorBo_vNext/texts/`, com identificadores estáveis para as unidades documentais. Dados de anotação adicionais são mantidos separadamente.

A interface pública é **somente para consulta**. A edição e a revisão dos dados são realizadas sobre os arquivos-fonte do corpus; índices, estatísticas e arquivos JSON utilizados pelo site são derivados desses dados.

## Universal Dependencies e CoNLL-U

O componente sintaticamente anotado segue o padrão **Universal Dependencies (UD)** e utiliza o formato **CoNLL-U**. O arquivo CoNLL-U canônico atualmente utilizado pelo projeto encontra-se em:

`CorBo/Corpus_Files/Bororo_UD_enriched_v5_plus_scripture.conllu`

Além das dez colunas do padrão CoNLL-U, os comentários e o campo `MISC` podem conter informações adicionais disponíveis para determinadas unidades ou tokens, incluindo traduções, forma ortográfica, glossa lexical e informação gramatical.

Entre os campos de enriquecimento encontrados no corpus estão:

| Campo | Descrição |
|---|---|
| `ORTHO` | forma ortográfica |
| `POS_FINE` | categoria gramatical mais detalhada |
| `GLOSS` | glossa lexical |
| `CLS` | informação de classe de posse, quando anotada |
| `PRCLITIC` | informação sobre proclíticos, quando anotada |

A análise morfológica é mantida separada da transcrição documental. A segmentação morfológica não deve ser inferida automaticamente a partir da grafia.

## Princípios editoriais

Um princípio central do CorBo é distinguir **evidência documental** de **intervenção editorial**. Por isso:

- a forma presente na fonte é preservada;
- uma forma revista pode ser registrada separadamente;
- irregularidades documentais, lacunas e numeração original não são corrigidas silenciosamente;
- unidades sem tradução podem permanecer no corpus;
- análises linguísticas e segmentações não são projetadas automaticamente sobre a fonte;
- índices e estatísticas são tratados como dados derivados e podem ser reconstruídos a partir das fontes do corpus.

Esse modelo permite utilizar o CorBo tanto para investigação linguística quanto para o estudo da história editorial e documental dos materiais em Bororo.

## Interface digital

A interface de consulta permite navegar pelas coleções e acessar formas do Bororo no contexto dos textos:

**https://languagestructure.github.io/Bororo-Corpus/**

A interface inclui páginas para textos, formas, morfemas, relações e estatísticas. Os recursos apresentados no site são gerados a partir dos dados mantidos neste repositório.

## Estado da versão 0.7

A versão 0.7 é uma **versão de pesquisa em desenvolvimento**. Diferentes coleções encontram-se em estágios distintos de revisão documental, ortográfica, tradutória e linguística. Algumas unidades ainda são provisórias e algumas coleções permanecem monolíngues ou parcialmente traduzidas.

Essa condição é representada nos dados sempre que possível, em vez de se produzir artificialmente uma versão inteiramente normalizada.

## Formatos

Os principais formatos utilizados no projeto são:

- **CoNLL-U** — anotação linguística e dependências;
- **TSV/CSV** — textos paralelos, camadas editoriais e dados tabulares;
- **JSON** — índices e recursos derivados utilizados pela interface;
- **TXT** — fontes e materiais documentais em texto simples.

## Língua e região

- **Língua:** Boe-Bororo
- **ISO 639-3:** `bor`
- **Tronco:** Macro-Jê
- **Região:** Mato Grosso, Brasil

## Licença e citação

O corpus é disponibilizado sob a licença **CC BY-NC-SA 4.0** (Atribuição–NãoComercial–CompartilhaIgual).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12110451.svg)](https://doi.org/10.5281/zenodo.12110451)

Ao utilizar o corpus em publicações, cite a versão específica consultada no Zenodo. Versões arquivadas no Zenodo fornecem um registro estável dos dados, enquanto o repositório e a interface pública podem continuar a receber atualizações.

## Autores

- **Fabrício Ferraz Gerardi**
- **Dolores Sollberger**
- **Lucas Toribio Serrano**

O CorBo é desenvolvido no âmbito da iniciativa **Boe eno moto**, dedicada à documentação, pesquisa, ensino e revitalização da língua Bororo.
