# Registro de mudanças

Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/). As versões publicadas
têm DOI próprio no Zenodo; cite sempre a versão consultada.

## [Não publicado]

## [0.10.1] — 2026-11-25 · DOI [10.5281/zenodo.24530404](https://doi.org/10.5281/zenodo.24530404)

### Textos
- Novo Testamento ***Pao Kurirewu Bataru Kurirewu*** (© 2019 Wycliffe Bible Translators), com a ortografia
  adaptada à do CorBo: 7.458 unidades de versículo e 823 títulos de seção em
  `CorBo_vNext/texts/pao-kurirewu-bataru/` (`scripts/import_pao_kurirewu_bataru.py`; relatório em
  `CorBo/validation/pao_kurirewu_bataru_import.tsv`). **Licença própria CC BY-NC-ND 4.0**, indicada no
  diretório, nas páginas e nos downloads; fica fora de `downloads/corbo-parallel.tsv` (CC BY 4.0) e tem
  arquivo próprio, `downloads/pao-kurirewu-bataru.tsv`.
- Leitor `pao-kurirewu-bataru.html` e **comparação paralela** `novo-testamento-paralelo.html`: as duas
  traduções do NT lado a lado, alinhadas por versículo (faixas de versículos agrupadas), com dados compactos
  por livro em `docs/data/nt-parallel/`.
- A nova coleção entra na busca e nas estatísticas do corpus documental (19.488 unidades no total).
- Estatísticas: seletor de **recorte** (todo o corpus, sem textos bíblicos, só textos bíblicos, só NT) para
  formas, n-grams, coleções e diversidade lexical (`statistics.html?recorte=nobib`); a seção "Textos bíblicos"
  inclui as duas traduções do NT. Sem os textos bíblicos: 2.374 unidades, 85.753 tokens, 9.588 formas.
- "Sobre" e página inicial: números do corpus lidos do resumo pré-calculado (antes fixos em 11.207 unidades)
  e menção às duas traduções do NT.

### Site
- Leitores: modo **Texto corrido** (Bororo e português lado a lado) além dos cartões; **vista interlinear**
  (forma, segmentação, glosa automática e link para a árvore) nas 346 unidades com sentença anotada
  (`scripts/build_interlinear.py` → `docs/data/interlinear.json`); pontuação colada à palavra na exibição;
  selo "provisória" único quando vale para todas as unidades (`docs/reader-view.js`).
- Painel lexical: contagem "ocorrências nos textos · com anotação linguística", homógrafos com índice
  sobrescrito, exemplos sem números de linha soltos.
- Página inicial: parágrafo sobre a língua e o povo, busca no topo, frase de exemplo em interlinear,
  coleções revistas (cantos Oieigo, textos bíblicos com AT e NT), ferramentas em três grupos (inclui
  árvores UD, tokenizador, cobertura e downloads) e números pré-calculados em vez de 33 arquivos.
- Glosa `onca_pintada` → `onça_pintada` no CoNLL-U.

### Anotação (CoNLL-U)
- **Causativas:** `=do` é o marcador causativo, clítico hospedado pelo índice pessoal; construção monoclausal com
  um só `nsubj` por verbo. O causado `PRON=do` passa a `iobj:agent` (ou `obl:agent`), com `Morph=<pessoa>=do`
  (`scripts/apply_causative_subjects.py`; 48 tokens em 47 frases, 4 gold).
- ***bito* 'matar':** verbo transitivo, `LEMMA=bito` em todo o paradigma, sem `Voice=Cau`
  (`scripts/apply_bito_lemma.py`; 131 tokens).
- Camada anotada sem outras mudanças: 12.020 unidades, 79.521 tokens, 1.900 sentenças gold, 706 erros de validação.

### Língua, fontes e metadados
- Nome da língua: ***Boe Ewadaru***. O Bororo é a única língua ainda falada da família Bororo; a associação ao
  tronco Macro-Jê foi retirada do site, do JSON-LD e do `.zenodo.json`.
- Proveniência do *Bakaru Maiwu* (Ochoa Camargo 1992) e autoria dos textos do Antigo Testamento (Pe. Ochoa com
  membros da comunidade de Meruri) registradas.
- Página inicial com mapa das terras indígenas Bororo.

### Integração contínua
- "Gerar índices do CorBo" voltou a funcionar: registra todos os arquivos gerados (JSON-LD, sitemap, OLAC,
  downloads) e usa `pull --rebase --autostash`; os fluxos que fazem push na `main` compartilham um grupo de
  `concurrency`.

## [0.10.0] — 2026-11-22 · DOI [10.5281/zenodo.24441715](https://doi.org/10.5281/zenodo.24441715)

### Licença e publicação
- Licença unificada em **CC BY 4.0** (README, site, CITATION.cff, OLAC e Zenodo). Até a v0.9.0 o README indicava CC BY-NC-SA 4.0 e o Zenodo, CC BY 4.0.
- `.zenodo.json`: registro do Zenodo passa a ser do tipo *dataset*; arquivo `LICENSE` adicionado.
- DOI conceitual (todas as versões) usado no site e no README: 10.5281/zenodo.12110451.

### Corpus e anotação
- Validação do CoNLL-U (`scripts/validate_conllu.py`) com relatório por linha e linha de base em CI.
- 7.179 correções automáticas sem ambiguidade (`CorBo/validation/safe_fixes.tsv`); erros de 4.893 para 3.706.
- Decisões de anotação de 21/11/2026: `Boe` (PROPN plural × NOUN singular), sufixo *-go* = `Voice=CauInc`,
  `Aspect=IncProg`, `Number=Sgtv` (singulativo), `dukeje` (SCONJ/`mark` × ADV/`advmod`), citações com `ako`
  (`ccomp` × `parataxis`); XPOS `conj` unificado em `cconj`.
- Camadas derivadas gold (1.778 sentenças) e silver (7.264), lista de revisão e painel de cobertura.
- Rascunho das convenções ortográficas e de normalização (`docs/ORTOGRAFIA.md`), com 7 pontos a decidir.
- Decisões ortográficas de 22/11/2026: só oxítonas de duas ou mais sílabas levam acento, que é mantido
  (lista de revisão em `CorBo/validation/acentos_revisao.tsv`); tokens de pontos reproduzem o `# text`
  (`..`, `...`, `.. .` = `..` + `.`; 408 sentenças); a forma decide `Boe` (PROPN, Plur) × `boe` (NOUN, Sing),
  111 tokens ajustados. Registro em `CorBo/validation/orthography_fixes_20261122.tsv`.
- Terceira rodada (22/11/2026): 15 pontuações com HEAD apontando para si mesmas passam a depender da raiz;
  86 FORMs alinhados ao `# text` (caixa e `_` → `-`). Erros de 824 para 792; gold 1.893 sentenças.
  As 202 sentenças em que texto e tokens divergem de fato estão em `CorBo/validation/texto_tokens_revisao.tsv`
  (`scripts/text_token_worksheet.py`), com coluna de decisão.
- Decisões de FFG sobre texto × tokens (22/11/2026, `scripts/apply_text_token_decisions.py`): *imedage* é o plural
  de *metuia* (21 tokens, `Number=Plur`); segue-se o texto em *paganure* (7); as formas com *oino* separadas são
  as corretas: 43 tokens fundidos divididos (*iroino* → *iro* + *oino*) e 7 textos fundidos separados
  (original em `# text_source`). Erros de 792 para 724; gold 1.894 sentenças.
- *Barogwato*/*Barogwatore* divididos em *barogwa* + *to*/*tore* (33 tokens; 26 textos separados); *Baadojeba*
  corrigido no texto (3); *tagaaregodure* → *tagaregodure* (3); rótulos *ref)*/*refl.)* removidos de 8 entradas
  do dicionário; caixa de 12 FORMs alinhada ao texto. Erros de 724 para 706.
- Busca por morfema passa a usar `Morph=` (de 29 para 28.604 ocorrências).

### Tokenizador
- Inventário v5: pré-tokenização, estado de revisão, suporte baixo, superfície × subjacente, suspeita de português.
- Planilha estratificada de 400 formas para o gold de avaliação; `scripts/compare_segmenters.py`
  (Morfessor, SentencePiece) pronto para quando o gold estiver anotado.
- Pacote Python `corbo-tokenizer` (pasta `python/`) e exportação TSV/JSON/CoNLL-U na página do tokenizador.
- Estado das análises indicado também por sublinhado (não só por cor).

### Site
- Painel lexical único (análise, segmentação, dicionário, exemplos, distribuição), com índice pré-calculado.
- Cabeçalho comum a todas as páginas; versão em inglês (início, sobre, como usar, downloads).
- Página de downloads; link permanente e "sugerir correção" em cada unidade dos leitores.
- Fonte Gentium Book Plus para o texto Bororo; estatísticas com visão geral pré-calculada e composição por tipo de material.
- Árvores UD exportáveis em SVG.
- schema.org/Dataset, `sitemap.xml`, `robots.txt` e registro OLAC (`docs/olac.xml`).
- Correções estruturais (22/11/2026): 303 fragmentos de alta confiança unidos à sentença anterior ou IDs renumerados; 94 fragmentos transformados em sentenças próprias (`<sent_id>#N`, `# text` reconstruído e marcado); FORM alinhado à caixa do `# text` em 1.591 sentenças (1.789 tokens, sobretudo Boe/boe); número de linha da fonte movido do `# text` para `# source_line` em 55 sentenças. Erros de 3.706 para 1.341; gold de 1.778 para 1.875 sentenças. Registros em `CorBo/validation/structural_applied_20261122.tsv` e `text_form_fixes_20261122.tsv`.
- Correções de árvore (22/11/2026, segunda rodada, `scripts/propose_tree_fixes.py`): IDs repetidos renumerados com HEADs remapeados (284 sentenças); DEPREL `root` em 180 sentenças cuja raiz estava rotulada com outra relação (verbos e frases de até duas palavras, como *Ca !*); UPOS preenchido em 42 tokens cuja forma tem classe inequívoca no corpus (`Auto=upos`). Erros de 1.341 para 835; gold 1.888 sentenças. Registro em `CorBo/validation/tree_applied_20261122.tsv`; 150 propostas de confiança média aguardam revisão em `tree_proposals.tsv`; demais erros listados em `manual_review.tsv`.
- Busca por padrão na Concordância: curingas `*` e `?`, expressões regulares `/…/` e lacunas `[]`/`[]{m,n}`; sequências destacadas inteiras.
- Correções: o status do visualizador UD ficava em "Carregando…"; dez leitores bíblicos (Salmos, Amós, Joel etc.) interrompiam o script por causa de um painel antigo inexistente.

### Documentação
- Guia de anotação, inventário de rótulos, mapa do tokenizador, ética e governança, proveniência das sentenças.

## [0.9.0] — 2026-10-17 · DOI [10.5281/zenodo.23441622](https://doi.org/10.5281/zenodo.23441622)
- Atualização do CoNLL-U a partir do arquivo de trabalho de 17/10/2026.
- Reconstrução dos índices públicos, do modelo lexical do tokenizador e do índice gramatical (ver `docs/RELEASE_NOTES_v0.9.0.md`).

## [0.8.0] — 2026-10-06 · DOI [10.5281/zenodo.23187959](https://doi.org/10.5281/zenodo.23187959)
- Índice público ampliado para 10.268 unidades, 242.229 tokens e 17.026 formas.
- Integração de Pemo–Coqueiro (261 unidades), Archive additions (226) e Archive parallel witnesses (305) após colação.
- Visualização UD restrita às sentenças anotadas no CoNLL-U autoritativo.
