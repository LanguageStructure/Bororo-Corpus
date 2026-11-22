# Registro de mudanças

Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/). As versões publicadas
têm DOI próprio no Zenodo; cite sempre a versão consultada.

## [Não publicado]

### Corpus e anotação
- Validação do CoNLL-U (`scripts/validate_conllu.py`) com relatório por linha e linha de base em CI.
- 7.179 correções automáticas sem ambiguidade (`CorBo/validation/safe_fixes.tsv`); erros de 4.893 para 3.706.
- Decisões de anotação de 21/11/2026: `Boe` (PROPN plural × NOUN singular), sufixo *-go* = `Voice=CauInc`,
  `Aspect=IncProg`, `Number=Sgtv` (singulativo), `dukeje` (SCONJ/`mark` × ADV/`advmod`), citações com `ako`
  (`ccomp` × `parataxis`); XPOS `conj` unificado em `cconj`.
- Camadas derivadas gold (1.778 sentenças) e silver (7.264), lista de revisão e painel de cobertura.
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
