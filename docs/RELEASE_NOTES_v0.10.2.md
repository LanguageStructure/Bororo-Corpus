# CorBo v0.10.2 — notas de lançamento

Data: 25 de novembro de 2026. DOI desta versão: a registrar após a publicação no Zenodo.
DOI de todas as versões: [10.5281/zenodo.12110451](https://doi.org/10.5281/zenodo.12110451).

## O que muda

Versão de correção. A única mudança na anotação é a segmentação dos pronomes causativos.

- **Causativo *-do* como sufixo.** Por decisão do autor (25/11/2026), o marcador causativo *-do* é tratado
  como sufixo do índice pessoal, e não como clítico. Os 48 pronomes com `Voice=Cau`, em 47 frases (4 delas
  gold: dic_0022, dic_0023, dic_0024, dic_1166), passam de `Morph=<pessoa>=do` a `Morph=<pessoa>-do`
  (ex.: *ure edo imaragodudo* 'ele fez eles me fazerem trabalhar', *edo* `e-do`).
- FORM, LEMMA, FEATS, HEAD e DEPREL não mudam. O `=do` do imperativo (*akaiwodo* `a=aiwo=do`) continua
  como clítico de modo.
- Script: `scripts/apply_causative_suffix_do.py` (simulação por padrão, `--apply` para gravar).
  Registro: `CorBo/validation/causative_do_suffix_20261125.tsv`. Guia: `docs/ANNOTATION_GUIDE.md`.

## Números (sem mudança em relação à v0.10.1)

- Corpus documental: 19.488 unidades, 539.117 tokens, 36 coleções.
- Camada anotada: 12.020 unidades (11.760 tokenizadas), 79.521 tokens; 1.900 sentenças gold (9.802 tokens);
  706 erros de validação; cerca de 70% dos tokens com algum valor atribuído automaticamente.

## Licença

CC BY 4.0, com a exceção do diretório `CorBo_vNext/texts/pao-kurirewu-bataru/` (CC BY-NC-ND 4.0), como na v0.10.1.
