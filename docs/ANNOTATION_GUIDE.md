# Guia de anotação do CorBo (CoNLL-U)

> **Estado:** rascunho de trabalho (novembro de 2026). As decisões descritas aqui
> refletem o que já está no arquivo canônico. Os pontos marcados **[DECIDIR]**
> exigem uma decisão do responsável pela anotação antes de serem tratados como norma.

Arquivo canônico: `CorBo/Corpus_Files/CorBo.conllu`.
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
| `propn` | PROPN | **[DECIDIR]** o lema `Boe` aparece como NOUN (1.123) e PROPN (682) |
| `v`, `vt`, `vi` | VERB | `vt`/`vi` marcam transitividade |
| `aux` | AUX | |
| `adv`, `advm` | ADV | |
| `posp` | ADP | posposições |
| `bi` | PRON | formas pronominais livres (série *bi*) |
| `pron` | PRON | |
| `dem`, `det`, `art` | DET | |
| `prcl` | PART | partículas |
| `conj` / `cconj` | CCONJ | **[DECIDIR]** unificar em um só XPOS |
| `sconj` | SCONJ | |
| `num` | NUM | |
| `intj` | INTJ | |
| `x`, `onom` | X | `onom` = onomatopeia |
| `punct` | PUNCT | |

Casos abertos: `dukeje` aparece como ADV (100) e SCONJ (86) conforme o XPOS atribuído — **[DECIDIR]** se há duas funções ou uma só.

## 4. DEPREL

Relações universais, sem subtipos por enquanto. Usos específicos do projeto:

- **posposições**: a posposição é `case` dependente do seu complemento nominal (`kugure ← ji`);
- **discurso citado**: com o verbo de dizer `ako` e o citativo `oino` (anotado como ADV) — **[DECIDIR]** `ccomp` ou `parataxis` para a citação; hoje ambos ocorrem no corpus (`ccomp` 2.633, `parataxis` 3.764, nem todos em citações);
- **`dep`** (823 tokens) deve ser tratado como pendência, não como análise final.

## 5. FEATS

Traços universais conforme o UD; os específicos do Bororo estão marcados como *CorBo* no inventário. Ordem alfabética das chaves (exigência UD). Rascunho das definições:

| Traço | Valores | Notas |
|---|---|---|
| `Person`, `Number` | 1/2/3; Sing/Plur | concordância e índices pessoais |
| `Clusivity` | In/Ex | 1ª pessoa do plural inclusiva/exclusiva |
| `Number=Sgtv` | — | **[DECIDIR]** confirmar valor e definição (singulativo?) |
| `Number=Col` | — | o UD usa `Coll`; **[DECIDIR]** renomear |
| `Mood` | Ind, Sub, Imp, Quot, Opt | `Qop`, `Qot`, `Imd`, `In` aparecem 1–3 vezes: prováveis erros |
| `Status=Irr` | — | irrealis (*CorBo*) |
| `Nomzr` | Rel, Loc | nominalizador (*CorBo*) |
| `Reflex=Yes` | — | prefixo correferente *t-* |
| `Deixis` | Prox, Med, Dist, Remt | |
| `Voice` | Cau, Pass, CauPass | `CPass`, `CauI`, `CauInc`, `IncCau`: **[DECIDIR]** |
| `Aspect` | Prog, Inc | `IncProg`, `IProg`: **[DECIDIR]** |
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
| `Morph=` | segmentação explícita (`-` afixo, `=` clítico). **[DECIDIR]** O guia de morfologia prevê `MORPH=`, mas o arquivo usa `Morph=` em 12.478 tokens: escolher uma grafia e documentá-la |
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
