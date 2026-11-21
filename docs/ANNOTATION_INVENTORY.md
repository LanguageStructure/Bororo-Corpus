# Inventário de rótulos do CorBo

> Gerado automaticamente por `scripts/build_annotation_inventory.py` a partir de `CorBo/Corpus_Files/CorBo.conllu`. Não edite à mão; edite as descrições no script.

Descrições marcadas *(a confirmar)* são rascunhos que dependem de revisão linguística.

## UPOS

| UPOS | Descrição | Tokens |
|---|---|---:|
| `PUNCT` | pontuação | 18244 |
| `VERB` | verbo | 15489 |
| `NOUN` | substantivo | 13779 |
| `ADV` | advérbio | 10273 |
| `ADP` | posposição | 7078 |
| `PRON` | pronome | 5393 |
| `PROPN` | nome próprio | 2755 |
| `DET` | determinante/artigo/demonstrativo | 2559 |
| `X` | outro / não classificado | 1429 |
| `PART` | partícula | 560 |
| `AUX` | auxiliar | 514 |
| `INTJ` | interjeição | 427 |
| `_` | **fora do UD — revisar** | 342 |
| `CCONJ` | conjunção coordenativa | 275 |
| `SCONJ` | conjunção subordinativa | 167 |
| `NUM` | numeral | 81 |
| `dukeje` | **fora do UD — revisar** | 1 |
| `reo` | **fora do UD — revisar** | 1 |

## XPOS (rótulos do projeto) → UPOS

| XPOS | UPOS observados |
|---|---|
| `punct` | `PUNCT` (18244) |
| `n` | `NOUN` (13732), `VERB` (10), `PROPN` (9), `ADV` (6), `PRON` (2), `NUM` (1), `X` (1), `ADP` (1) |
| `v` | `VERB` (12027), `NOUN` (43), `ADV` (8) |
| `adv` | `ADV` (10228), `NOUN` (1), `PRON` (1) |
| `posp` | `ADP` (7072), `ADV` (2), `VERB` (1), `NOUN` (1) |
| `bi` | `PRON` (4615), `PROPN` (1) |
| `propn` | `PROPN` (2742), `NOUN` (2) |
| `vt` | `VERB` (2025) |
| `dem` | `DET` (2000) |
| `x` | `X` (1422), `AUX` (8) |
| `vi` | `VERB` (1424) |
| `pron` | `PRON` (769), `PROPN` (3) |
| `prcl` | `PART` (560) |
| `aux` | `AUX` (506) |
| `det` | `DET` (464) |
| `intj` | `INTJ` (427) |
| `_` | `_` (342), `ADV` (1), `dukeje` (1) |
| `conj` | `CCONJ` (225) |
| `sconj` | `SCONJ` (167) |
| `art` | `DET` (94) |
| `num` | `NUM` (80) |
| `cconj` | `CCONJ` (50) |
| `advm` | `ADV` (26) |
| `onom` | `X` (6) |
| `adp` | `ADP` (4) |
| `bu` | `PRON` (3) |
| `p` | `PRON` (2), `ADP` (1) |
| `dir` | `ADV` (2) |
| `vz` | `VERB` (1) |
| `Definite=Ind|PronType=Art` | `DET` (1) |
| `i` | `PRON` (1) |
| `b` | `VERB` (1) |
| `AUX` | `reo` (1) |

## DEPREL

| DEPREL | Tokens |
|---|---:|
| `punct` | 18303 |
| `root` | 11219 |
| `advmod` | 9621 |
| `nsubj` | 8631 |
| `obl` | 6908 |
| `parataxis` | 3764 |
| `case` | 3650 |
| `nmod` | 3480 |
| `_` | 3055 |
| `ccomp` | 2633 |
| `det` | 2142 |
| `obj` | 2017 |
| `flat` | 950 |
| `dep` | 823 |
| `conj` | 764 |
| `aux` | 453 |
| `discourse` | 312 |
| `cc` | 263 |
| `xcomp` | 116 |
| `mark` | 83 |
| `appos` | 64 |
| `advcl` | 55 |
| `dislocated` | 22 |
| `vocative` | 13 |
| `iobj` | 12 |
| `acl` | 5 |
| `fixed` | 2 |
| `nummod` | 2 |
| `comp` | 1 |
| `15` | 1 |
| `6` | 1 |
| `cae` | 1 |
| `5` | 1 |

## FEATS

| Traço | Valor | Origem | Descrição | Tokens |
|---|---|---|---|---:|
| `Aspect` | `Inc` | CorBo | incoativo (a confirmar) | 96 |
| `Aspect` | `IncProg` | CorBo | (sem descrição) | 3 |
| `Aspect` | `Prog` | UD | progressivo | 436 |
| `Clusivity` | `Ex` | UD | exclusivo | 2603 |
| `Clusivity` | `In` | UD | inclusivo | 929 |
| `Clusivity` | `Ind` | CorBo | (sem descrição) | 3 |
| `Definite` | `Ind` | UD | indefinido | 563 |
| `Degree` | `Aug` | UD | aumentativo | 3 |
| `Degree` | `Dim` | UD | diminutivo | 528 |
| `Deixis` | `Dist` | UD | distal | 9 |
| `Deixis` | `Med` | UD | medial | 1508 |
| `Deixis` | `Prox` | UD | proximal | 434 |
| `Deixis` | `Remt` | UD | remoto (a confirmar) | 1 |
| `Dub` | `Yes` | CorBo | (sem descrição) | 3 |
| `Emph` | `Yes` | UD | enfático (a confirmar) | 39 |
| `Gender` | `Fem` | UD | feminino (empréstimos?) | 5 |
| `Gender` | `Masc` | UD | masculino (empréstimos?) | 1 |
| `Int` | `Yes` | CorBo | interrogativo (a confirmar; considerar PronType=Int ou Mood=Int) | 18 |
| `Mood` | `Imp` | UD | imperativo | 232 |
| `Mood` | `Ind` | UD | indicativo | 14887 |
| `Mood` | `Opt` | UD | optativo | 36 |
| `Mood` | `Qop` | CorBo | (sem descrição) | 3 |
| `Mood` | `Quot` | UD | quotativo (a confirmar) | 77 |
| `Mood` | `Sub` | UD | subjuntivo/dependente (a confirmar) | 848 |
| `Nomzr` | `Loc` | CorBo | nominalização locativa (a confirmar) | 10 |
| `Nomzr` | `Rel` | CorBo | nominalização relativa (a confirmar) | 632 |
| `Number` | `Col` | CorBo | coletivo (a confirmar; o UD usa `Coll`) | 3 |
| `Number` | `Plur` | UD | plural | 11140 |
| `Number` | `Sgtv` | UD | singulativo (a confirmar) | 256 |
| `Number` | `Sing` | UD | singular | 21207 |
| `Number[psor]` | `Plur` | UD | possuidor plural | 17 |
| `Number[psor]` | `Sing` | UD | possuidor singular | 36 |
| `Person` | `1` | UD | primeira pessoa | 8945 |
| `Person` | `2` | UD | segunda pessoa | 1930 |
| `Person` | `3` | UD | terceira pessoa | 18527 |
| `Person[psor]` | `1` | UD | possuidor de 1ª pessoa | 39 |
| `Person[psor]` | `2` | UD | possuidor de 2ª pessoa | 1 |
| `Person[psor]` | `3` | UD | possuidor de 3ª pessoa | 29 |
| `Polarity` | `Neg` | UD | negativo | 1125 |
| `PronType` | `Art` | UD | artigo | 561 |
| `PronType` | `Dem` | UD | demonstrativo | 85 |
| `PronType` | `Ind` | UD | indefinido | 33 |
| `PronType` | `Int` | UD | interrogativo | 96 |
| `PronType` | `Prs` | UD | pessoal | 361 |
| `PronType` | `Rcp` | UD | recíproco | 52 |
| `PronType` | `Tot` | UD | total/coletivo | 44 |
| `Reflex` | `Yes` | UD | reflexivo / correferente com o sujeito (prefixo t-) (a confirmar) | 1264 |
| `Speech` | `Ind` | CorBo | discurso indireto (a confirmar) | 113 |
| `Speech` | `IndTrans` | CorBo | (a definir) | 5 |
| `Speech` | `Quo` | CorBo | discurso citado (a confirmar) | 33 |
| `Status` | `Irr` | CorBo | irrealis (a confirmar) | 1010 |
| `VerbForm` | `Ger` | UD | gerúndio/forma adverbial (a confirmar) | 149 |
| `Voice` | `CPass` | CorBo | (sem descrição) | 3 |
| `Voice` | `Cau` | UD | causativo | 1913 |
| `Voice` | `CauPass` | CorBo | causativo-passivo (a confirmar) | 11 |
| `Voice` | `Pass` | UD | passivo | 71 |

## Valores raros ou não documentados (revisar)

| Traço | Valor | Tokens |
|---|---|---:|
| `` | `Sing` | 1 |
| `Aspect` | `IProg` | 1 |
| `Clusivity[psor]` | `Ex` | 1 |
| `Mod` | `Imp` | 2 |
| `Mod` | `Ind` | 1 |
| `Mood` | `Imd` | 1 |
| `Mood` | `In` | 1 |
| `Mood` | `Qot` | 2 |
| `Number` | `≈` | 1 |
| `Person` | `21` | 1 |
| `Person` | `S` | 1 |
| `Plur` | `3` | 1 |
| `PronType` | `Adv` | 1 |
| `PronType` | `Med` | 1 |
| `Voice` | `CauI` | 2 |
| `Voice` | `CauInc` | 1 |
| `Voice` | `IncCau` | 2 |
