## 📜 Corpus bíblico (Bororo)

Este apêndice reúne livros do Antigo e do Novo Testamento em Bororo, convertidos para:
- `bororo_scripture_parallel.csv` (linha por versículo; `source, book, chapter, verse, bororo, portugues`)
- `bororo_scripture_meta.tsv` (metadados por obra)
- `Bororo_UD_enriched_v5_scripture.conllu` (uma sentença por versículo, com `# meta:`: `sourcefile, book, chapter, verse, genre=scripture`)

**Heurística de capítulos/versos**  
Arquivos `.txt` (padrão `_2-orthophon`) foram analisados por regras simples:
- capítulos reconhecidos por linhas do tipo `1.` ou `1`;
- versos como `1. texto`; quando ausente, cada parágrafo vira um verso sequencial;
- `sent_id` = `<PREFIXO>.<cap>.<verso>` (ex.: `GEN.1.1`, `PSA.23.1`, `JOS.3.7`).

Traduções (`translation_pt` / `translation_en`) permanecem vazias, a serem revisadas e preenchidas posteriormente.


## Relação com o CoNLL-U autoritativo

Os arquivos CoNLL-U bíblicos descritos acima são derivados documentais históricos e permanecem disponíveis como recursos separados. Eles **não** constituem o treebank autoritativo usado atualmente pelo visualizador UD, pela análise de formas ou pelos índices morfossintáticos do site.

A fonte CoNLL-U autoritativa atual é:

`exemplosDicBor_full_review_pass17_incomplete_first.conllu`

O pipeline público não deve combinar automaticamente sentenças bíblicas com esse arquivo para produzir árvores de dependência.