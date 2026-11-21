# Guia de anotação do CorBo (CoNLL-U)

> **Estado:** rascunho de trabalho (novembro de 2026). As decisões descritas aqui
> refletem o que já está no arquivo canônico. Os pontos marcados **[DECIDIR]**
> exigem uma decisão do responsável pela anotação antes de serem tratados como norma.

Arquivo canônico: `CorBo/Corpus_Files/CorBo.conllu`.
Responsável pela anotação manual e pelas correções do CoNLL-U: **Fabrício Ferraz Gerardi** (FFG). Toda anotação sem marca de automática (§6) é dele.
Inventário completo (gerado automaticamente, com contagens): [`ANNOTATION_INVENTORY.md`](ANNOTATION_INVENTORY.md).
Convenção de segmentação morfológica: [`MORPHOLOGY_ANNOTATION.md`](MORPHOLOGY_ANNOTATION.md).
Princípios editoriais das fontes: [`../CorBo_vNext/schema/EDITORIAL_GUIDELINES.md`](../CorBo_vNext/schema/EDITORIAL_GUIDELINES.md).

---

## 1. Princípios

1. **A forma documental é intocável.** `FORM` reproduz a grafia da fonte. Normalização, correção e análise ficam em outras colunas ou camadas.
2. **Anotação manual e automática são distinguíveis no próprio arquivo** (ver §6). Nenhum campo automático é apresentado como revisado.
3. **Ausência não é análise.** `_` significa "não anotado nesta camada", não "vazio" nem "simples".
4. **Arquitetura UD quando aplicável.** UPOS e DEPREL seguem o inventário universal; traços específicos do Bororo são documentados aqui e no inventário.

## 2. Estrutura de uma sentença

```
# sent_id = boe_ero_01_01
# text = Oinore Boe egore tore kugure ji , Boe erore tore kugure ji .
# text_por = É desse jeito que os bororo falam com seus filhinhos, …
# text_eng = …
1	Oinore	oino	ADV	adv	_	3	advmod	_	Morph=oino=re
…
```

| Comentário | Obrigatório | Conteúdo |
|---|---|---|
| `sent_id` | sim | identificador único e estável (ver §7) |
| `text` | sim | texto da sentença; deve coincidir com a concatenação das formas, salvo espaços |
| `text_por`, `text_eng` | não | traduções livres |
| `source_conllu` | não | arquivo CoNLL-U de origem antes da unificação |
| `source_unit`, `section` | não | unidade e seção na fonte documental (Boe Ero) |
| `auto_annotation`, `auto_fields`, `auto_tokens`, `auto_note` | quando houver campos automáticos | ver §6 |
| `model_projection` | não | sentença gold de onde a análise foi projetada e similaridade |
| `sent_id_original` | não | identificador anterior, quando a sentença foi dividida (`X#2`, `X#3`…) |

**Regras estruturais** (verificadas por `scripts/validate_conllu.py`):

- uma linha em branco separa sentenças — **nunca** dentro de uma sentença; um bloco sem `# sent_id` é tratado como fragmento e é erro;
- IDs de token `1..n`, sem lacunas nem repetições;
- `HEAD` inteiro que aponta para um token existente ou `0`; exatamente uma raiz (`HEAD=0` ⇔ `DEPREL=root`); sem ciclos;
- sintaxe parcial é permitida no arquivo de trabalho, mas a sentença não entra na camada gold.

## 3. UPOS e XPOS

`UPOS` usa somente as 17 etiquetas universais. `XPOS` guarda a etiqueta do projeto. Correspondência em uso:

| XPOS (projeto) | UPOS | Observação |
|---|---|---|
| `n` | NOUN | |
| `propn` | PROPN | `Boe` = "os Bororo" → PROPN, `Number=Plur`; outras acepções → NOUN, `Number=Sing` (decidido em 21/11/2026) |
| `v`, `vt`, `vi` | VERB | `vt`/`vi` marcam transitividade |
| `aux` | AUX | |
| `adv`, `advm` | ADV | |
| `posp` | ADP | posposições |
| `bi` | PRON | formas pronominais livres (série *bi*) |
| `pron` | PRON | |
| `dem`, `det`, `art` | DET | |
| `prcl` | PART | partículas |
| `cconj` | CCONJ | `conj` foi unificado em `cconj` em 21/11/2026 |
| `sconj` | SCONJ | |
| `num` | NUM | |
| `intj` | INTJ | |
| `x`, `onom` | X | `onom` = onomatopeia |
| `punct` | PUNCT | |

`dukeje` tem duas funções (decidido em 21/11/2026): **SCONJ** com `DEPREL=mark` quando introduz oração subordinada; **ADV** com `DEPREL=advmod` nos demais casos. 317 tokens já seguem a regra; 67 combinações incoerentes (64 automáticas), como SCONJ+obl ou ADV+parataxis, estão listadas em `CorBo/validation/dukeje_review.tsv` para revisão.

## 4. DEPREL

Relações universais, sem subtipos por enquanto. Usos específicos do projeto:

- **posposições**: a posposição é `case` dependente do seu complemento nominal (`kugure ← ji`);
- **discurso citado** (decidido em 21/11/2026): os complementos oracionais de `ako` ('dizer') são `ccomp`; quando a oração citada tem seu próprio verbo principal, como frase independente, a relação é `parataxis`. A regra exige leitura caso a caso e não foi aplicada automaticamente (hoje: 2.128 `ccomp` e 448 `parataxis` dependentes de `ako`);
- **`dep`** (823 tokens) deve ser tratado como pendência, não como análise final.

## 5. FEATS

Traços universais conforme o UD; os específicos do Bororo estão marcados como *CorBo* no inventário. Ordem alfabética das chaves (exigência UD). Rascunho das definições:

| Traço | Valores | Notas |
|---|---|---|
| `Person`, `Number` | 1/2/3; Sing/Plur | concordância e índices pessoais |
| `Clusivity` | In/Ex | 1ª pessoa do plural inclusiva/exclusiva |
| `Number=Sgtv` | — | singulativo (formas em *-du/-edu*: *baraedu*, *imedu*, *onaregedu*) |
| `Number=Col` | — | 3 tokens; o UD usa `Coll` — **[DECIDIR]** (pendente com os valores raros) |
| `Mood` | Ind, Sub, Imp, Quot, Opt | **[DECIDIR]** `Qop`, `Qot`, `Imd`, `In` (1–3 tokens cada) — em resolução pelo anotador |
| `Status=Irr` | — | irrealis (*CorBo*) |
| `Nomzr` | Rel, Loc | nominalizador (*CorBo*) |
| `Reflex=Yes` | — | prefixo correferente *t-* |
| `Deixis` | Prox, Med, Dist, Remt | |
| `Voice` | Cau, Pass, CauPass, CauInc | `CauInc` = causativo-incoativo, sufixo *-go* (`CauI` e `IncCau` unificados em 21/11/2026); **[DECIDIR]** `CPass` (3 tokens) |
| `Aspect` | Prog, Inc, IncProg | `IncProg` = incoativo-progressivo (*-godu-* + *-nu-*, ex.: *paburedugodunure*); `IProg` corrigido para `IncProg` em 21/11/2026 |
| `Speech` | Ind, Quo, IndTrans | `Speech=Quo` licencia a evidência de *-iagu* (ver MORPHOLOGY_ANNOTATION.md) |
| `Person[psor]`, `Number[psor]` | — | traços do possuidor (camada `[psor]`, formato UD) |

## 6. Anotação automática

| Marca | Nível | Significado |
|---|---|---|
| `# auto_annotation = pendente de revisão manual` | sentença | há campos automáticos não revisados |
| `# auto_fields = lemma,upos,…` | sentença | quais colunas foram preenchidas |
| `Auto=lemma+upos+…` | token (MISC) | colunas preenchidas automaticamente neste token |
| `AutoLowConf=Yes` | token (MISC) | previsão de baixa confiança |
| `PosMorphAnnot=AI:…` | token (MISC) | anotação morfológica sugerida por IA |

Ao revisar um token, **remova** a marca correspondente. Uma sentença só entra na camada **gold** quando não restar nenhuma dessas marcas, a sintaxe estiver completa e o validador não acusar erro.

## 7. MISC

| Chave | Uso |
|---|---|
| `Morph=` | segmentação explícita (`-` afixo, `=` clítico; `0` = morfema zero). Grafia usada no arquivo (12.478 tokens); o build aceita `MORPH=` e `Morph=` e alimenta a busca por morfema do site |
| `Gloss=` | glosa (o campo foi criado para glosas soltas que estavam sem chave) |
| `Auto=`, `AutoLowConf=`, `PosMorphAnnot=` | ver §6 |

## 8. Identificadores

`sent_id` precisa ser único e estável entre versões. Os grupos atuais (`boe_ero_…`, `dic_…`, `Jussila-…`, numéricos `NNN-N`) estão listados com contagens em `CorBo/validation/sent_id_groups.tsv`, com colunas a preencher (coleção, fonte, gênero) para que a proveniência seja registrada sem ser inferida do conteúdo.

## 9. Fluxo de trabalho

```bash
python3 scripts/validate_conllu.py CorBo/Corpus_Files/CorBo.conllu \
    --report CorBo/validation/issues.tsv --summary CorBo/validation/summary.json
python3 scripts/fix_conllu_safe.py CorBo/Corpus_Files/CorBo.conllu --log CorBo/validation/safe_fixes.tsv          # simulação
python3 scripts/fix_conllu_safe.py CorBo/Corpus_Files/CorBo.conllu --log CorBo/validation/safe_fixes.tsv --apply  # grava
python3 scripts/build_annotation_inventory.py
python3 scripts/split_gold_silver.py
cp CorBo/validation/summary.json CorBo/validation/baseline.json   # depois de corrigir erros
```
