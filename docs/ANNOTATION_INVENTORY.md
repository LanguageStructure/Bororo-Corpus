# Inventário de rótulos do CorBo

> Gerado automaticamente por `scripts/build_annotation_inventory.py` a partir de `CorBo/Corpus_Files/CorBo.conllu`. Não edite à mão; edite as descrições no script.

Descrições marcadas *(a confirmar)* são rascunhos que dependem de revisão linguística.

## UPOS

| UPOS | Descrição | Tokens |
|---|---|---:|
| `PUNCT` | pontuação | 18357 |
| `VERB` | verbo | 15503 |
| `NOUN` | substantivo | 13703 |
| `ADV` | advérbio | 10275 |
| `ADP` | posposição | 7079 |
| `PRON` | pronome | 5383 |
| `PROPN` | nome próprio | 2859 |
| `DET` | determinante/artigo/demonstrativo | 2560 |
| `X` | outro / não classificado | 1430 |
| `PART` | partícula | 560 |
| `AUX` | auxiliar | 514 |
| `INTJ` | interjeição | 427 |
| `_` | **fora do UD — revisar** | 299 |
| `CCONJ` | conjunção coordenativa | 275 |
| `SCONJ` | conjunção subordinativa | 167 |
| `NUM` | numeral | 81 |
| `dukeje` | **fora do UD — revisar** | 1 |
| `reo` | **fora do UD — revisar** | 1 |

## XPOS (rótulos do projeto) → UPOS

| XPOS | UPOS observados |
|---|---|
| `punct` | `PUNCT` (18355) |
| `n` | `NOUN` (13642), `VERB` (10), `ADV` (6), `PROPN` (5), `PRON` (2), `NUM` (1), `X` (1), `ADP` (1) |
| `v` | `VERB` (12026), `NOUN` (43), `ADV` (8) |
| `adv` | `ADV` (10228), `NOUN` (1), `PRON` (1) |
| `posp` | `ADP` (7070), `ADV` (2), `VERB` (1), `NOUN` (1) |
| `bi` | `PRON` (4614), `PROPN` (1) |
| `propn` | `PROPN` (2850) |
| `vt` | `VERB` (2025) |
| `dem` | `DET` (2000) |
| `x` | `X` (1422), `AUX` (8) |
| `vi` | `VERB` (1424) |
| `pron` | `PRON` (759), `PROPN` (2) |
| `prcl` | `PART` (560) |
| `aux` | `AUX` (506) |
| `det` | `DET` (464) |
| `intj` | `INTJ` (427) |
| `_` | `_` (299), `NOUN` (16), `VERB` (15), `ADV` (3), `ADP` (3), `PUNCT` (2), `DET` (1), `dukeje` (1), `X` (1), `PRON` (1), `PROPN` (1) |
| `cconj` | `CCONJ` (275) |
| `sconj` | `SCONJ` (167) |
| `art` | `DET` (94) |
| `num` | `NUM` (80) |
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
| `punct` | 18337 |
| `root` | 11399 |
| `advmod` | 9477 |
| `nsubj` | 8619 |
| `obl` | 6905 |
| `parataxis` | 3764 |
| `case` | 3648 |
| `nmod` | 3479 |
| `_` | 3135 |
| `ccomp` | 2624 |
| `det` | 2141 |
| `obj` | 2016 |
| `flat` | 945 |
| `dep` | 822 |
| `conj` | 764 |
| `aux` | 451 |
| `discourse` | 311 |
| `cc` | 263 |
| `xcomp` | 116 |
| `mark` | 82 |
| `appos` | 61 |
| `advcl` | 54 |
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
| `Aspect` | `Inc` | CorBo | incoativo | 96 |
| `Aspect` | `IncProg` | CorBo | incoativo-progressivo (-godu- + -nu-) | 4 |
| `Aspect` | `Prog` | UD | progressivo | 436 |
| `Clusivity` | `Ex` | UD | exclusivo | 2602 |
| `Clusivity` | `In` | UD | inclusivo | 929 |
| `Clusivity` | `Ind` | CorBo | (sem descrição) | 3 |
| `Definite` | `Ind` | UD | indefinido | 563 |
| `Degree` | `Aug` | UD | aumentativo | 3 |
| `Degree` | `Dim` | UD | diminutivo | 528 |
| `Deixis` | `Dist` | UD | distal | 9 |
| `Deixis` | `Med` | UD | medial | 1507 |
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
| `Number` | `Plur` | UD | plural | 11124 |
| `Number` | `Sgtv` | CorBo | singulativo (formas em -du/-edu: baraedu, imedu, onaregedu) | 256 |
| `Number` | `Sing` | UD | singular | 21260 |
| `Number[psor]` | `Plur` | UD | possuidor plural | 17 |
| `Number[psor]` | `Sing` | UD | possuidor singular | 36 |
| `Person` | `1` | UD | primeira pessoa | 8944 |
| `Person` | `2` | UD | segunda pessoa | 1929 |
| `Person` | `3` | UD | terceira pessoa | 18525 |
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
| `PronType` | `Tot` | UD | total/coletivo | 41 |
| `Reflex` | `Yes` | UD | reflexivo / correferente com o sujeito (prefixo t-) (a confirmar) | 1264 |
| `Speech` | `Ind` | CorBo | discurso indireto (a confirmar) | 113 |
| `Speech` | `IndTrans` | CorBo | (a definir) | 5 |
| `Speech` | `Quo` | CorBo | discurso citado (a confirmar) | 33 |
| `Status` | `Irr` | CorBo | irrealis (a confirmar) | 1010 |
| `VerbForm` | `Ger` | UD | gerúndio/forma adverbial (a confirmar) | 149 |
| `Voice` | `CPass` | CorBo | (sem descrição) | 3 |
| `Voice` | `Cau` | UD | causativo | 1913 |
| `Voice` | `CauInc` | CorBo | causativo-incoativo, sufixo -go (ex.: epemegago, itaidugo) | 5 |
| `Voice` | `CauPass` | CorBo | causativo-passivo (a confirmar) | 11 |
| `Voice` | `Pass` | UD | passivo | 71 |

## Valores raros ou não documentados (revisar)

| Traço | Valor | Tokens |
|---|---|---:|
| `` | `Sing` | 1 |
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
