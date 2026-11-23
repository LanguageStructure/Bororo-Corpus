# CorBo v0.10.0 — notas de lançamento

**Data:** 22 de novembro de 2026 · **DOI desta versão:** [10.5281/zenodo.24441715](https://doi.org/10.5281/zenodo.24441715) · **Licença:** CC BY 4.0 · **DOI de todas as versões:** [10.5281/zenodo.12110451](https://doi.org/10.5281/zenodo.12110451)

## Em números

| | |
|---|---:|
| Unidades no CoNLL-U | 12.020 |
| Sentenças tokenizadas | 11.760 (79.521 tokens) |
| Sentenças **gold** (anotação manual, sintaxe completa, sem erros estruturais) | 1.900 (9.802 tokens) |
| Sentenças **silver** (estruturalmente válidas, com anotação automática) | 8.980 |
| Sentenças a revisar | 880 |
| Unidades aguardando tokenização | 260 |
| Erros de validação | 706 (eram 4.893 no início de novembro) |

## Principais mudanças

- **Validação do CoNLL-U** (`scripts/validate_conllu.py`) com relatório por linha e linha de base no CI: nenhuma categoria de erro pode aumentar.
- **Camadas gold e silver** derivadas do arquivo canônico (`CorBo/Corpus_Files/splits/`).
- **Correções registradas** em `CorBo/validation/`, cada uma com data e regra: correções seguras, fragmentos, IDs, raízes, UPOS, alinhamento texto × tokens.
- **Decisões de anotação e de ortografia** documentadas em `docs/ANNOTATION_GUIDE.md` e `docs/ORTOGRAFIA.md`:
  - o FORM segue o `# text`;
  - *Boe* (PROPN, plural) × *boe* (NOUN, singular);
  - o acento só aparece em oxítonas;
  - as reticências são tokenizadas como no texto;
  - formas com *oino* são separadas, e *barogwa to* também.
- **Tokenizador v5** e pacote Python `corbo-tokenizer`.
- **Site:**
  - painel lexical único, cabeçalho comum, versão em inglês e página de downloads;
  - busca por padrão e por morfema;
  - árvores UD exportáveis em SVG;
  - link permanente e "sugerir correção" em cada unidade.
- **Metadados:** schema.org/Dataset, sitemap, registro OLAC, `CITATION.cff`, `.zenodo.json` e `LICENSE`.
- **Licença unificada em CC BY 4.0.** Até a v0.9.0, o README indicava CC BY-NC-SA 4.0 e o Zenodo, CC BY 4.0.

## Limitações conhecidas

- **Traduções:** parte dos `# text_por` está em linhas trocadas e passa por revisão manual. Não use os pares Bororo–português como alinhamento verificado.
- **Camada silver:** é anotação automática (cerca de 70% dos tokens têm algum campo automático, marcado com `Auto=`, `AutoLowConf=` ou `PosMorphAnnot=AI`).
- **Erros e divergências:** os 706 erros de validação e as 116 sentenças com texto ≠ tokens estão listados para revisão (`manual_review.tsv`, `texto_tokens_revisao.tsv`).
- **Ética e proveniência:** campos ainda em preenchimento (`docs/ETICA_E_GOVERNANCA.md`).
- **Ortografia:** há decisões pendentes, como os caracteres de fonte antiga do *Boe Ero* e a revisão dos acentos.

Critérios para a 1.0: [`docs/ROADMAP_1.0.md`](ROADMAP_1.0.md).
