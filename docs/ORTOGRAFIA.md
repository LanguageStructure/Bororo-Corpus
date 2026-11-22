# Convenções ortográficas e de normalização do CorBo

> **Rascunho de 22/11/2026, a revisar por FFG** (atualizado no mesmo dia com as decisões sobre acento, reticências e Boe/boe). O que está aqui descreve o que o corpus **já faz**,
> com números extraídos do `CorBo.conllu`. Os pontos marcados **[DECIDIR]** precisam de decisão
> antes de virar regra. Este documento complementa o [guia de anotação](ANNOTATION_GUIDE.md),
> as [convenções de morfologia](MORPHOLOGY_ANNOTATION.md) e as
> [diretrizes editoriais do CorBo vNext](../CorBo_vNext/schema/EDITORIAL_GUIDELINES.md).

## 1. Princípio: a grafia da fonte é preservada

1. O `# text` e o `FORM` reproduzem a grafia do testemunho documental, com variação, acentos,
   caixa e pontuação. Nada é "corrigido" para facilitar a busca ou a análise.
2. Desde 22/11/2026, o `FORM` segue exatamente o `# text`, inclusive na caixa (ver guia de anotação).
3. Qualquer normalização é uma **camada derivada**: serve para busca, contagem e léxico, é recalculada
   pelos scripts e nunca substitui `FORM` nem `# text`.
4. O lema (`LEMMA`) é a forma de citação escolhida pelo anotador, sem acento e em minúsculas,
   exceto nomes próprios e `Boe` como etnônimo (ver guia de anotação).

## 2. Codificação

- UTF-8 sem BOM, em forma normalizada **NFC** (verificado: o arquivo inteiro já está em NFC).
  Scripts que gravam o CoNLL-U devem normalizar para NFC antes de escrever.
- **Caracteres de uso privado** (U+F063, U+F086, U+F087) aparecem em 7 frases do *Boe Ero*
  (`boe_ero_02_27`, `02_35`, `04_09`, `04_11`, `04_19`, `07_11`, `07_60`), dentro de palavras como
  *Koare* e no início de *ere*. São resíduos de uma fonte tipográfica antiga: o caractere
  real foi perdido na conversão. Ficam como estão, e o validador os aponta como erro.
  **[DECIDIR]** Qual letra cada um representa, conferindo na edição impressa do *Boe Ero*.

## 3. Inventário de letras

Nas palavras Bororo do corpus ocorrem 17 letras, em ordem de frequência:

> e o a r u i d g k t w b m j c n p

As letras **s h l f v q z x y** somam menos de 1.300 ocorrências e aparecem quase só em:

- empréstimos e palavras do português (*caminhão*, *café*, *missa*, *finado*, *mestre*, *inspetor*, *sal*);
- nomes próprios (*César*, *José*, *Simão*, *Xavantina*);
- interjeições e onomatopeias (*hm*, *hu*, *ha*, *ah*, *psiu*).

Algumas formas híbridas recebem morfologia Bororo e mantêm a grafia portuguesa da base:
*caminhãoto*, *mestredoge*, *cafece*.

**[DECIDIR]** Incluir aqui uma tabela grafema–fonema (por exemplo, o valor de *c*, *j*, *r* e *w*) e
a referência da ortografia salesiana em que as fontes se baseiam.

### Alternâncias iniciais

Depois de prefixo pessoal, a consoante inicial do radical alterna na escrita. O tokenizador só usa
essas alternâncias quando a forma prefixada está atestada (`scripts/bororo_initial_alternations.py`):

| Radical | Depois de prefixo | Estatuto |
|---|---|---|
| b | w | geral |
| p | b | padrão, com exceções lexicais |
| t | d | padrão, com exceções lexicais |
| k | g | padrão, com exceções lexicais |
| c | j | padrão, com exceções lexicais |

Essas alternâncias **não** são normalizadas: *ako* e *egore* continuam formas distintas, ligadas pelo lema.

### Vogais duplas

Sequências de vogal igual (*eejore*, *jii*, *ii*) ocorrem em cerca de 1.400 frases e são mantidas
como estão. Elas não são tratadas como erro de digitação nem reduzidas na camada normalizada.

## 4. Diacríticos

**Regra (FFG, 22/11/2026): em Bororo só se acentuam as oxítonas de duas ou mais sílabas.** O acento
agudo marca a sílaba tônica final. É portanto **significativo**: fica no `FORM` e não é removido na
camada normalizada.

A grande maioria das palavras Bororo é paroxítona e se escreve sem acento. Os diacríticos do corpus
aparecem em três situações.

**Palavras portuguesas** mantêm a grafia do português: *caminhão* (71), *João*, *café*, *você*, *não*,
*pátio*, *cemitério*.

**Oxítonas Bororo acentuadas, conforme a regra:** *icá*, *aró*, *akó*, *kodibá*, *kupé*, *tododó*,
*pejó*. Várias também aparecem sem acento:

| Sem acento | Com acento |
|---|---|
| ica (46) | icá (29) |
| aro (17) | aró (11) |
| ako (47) | akó (3) |
| kodiba (15) | kodibá (3) |
| pejo (3) | pejó (2), pejô (4) |

A forma sem acento pode ser uma grafia que omitiu o acento ou uma palavra diferente (paroxítona). Só o contexto decide.

**Casos que contrariam a regra:**

- monossílabos acentuados: *mè*, *mé*, *wè* e talvez *cá*, *tá*, *pá*, que podem ser portugueses;
- acento fora da última sílaba: *pojôrogu*, *karajánure* (base portuguesa *Karajá*);
- circunflexo e grave em vez de agudo: *pejô*, *mè*, *wè*.

`scripts/review_accents.py` gera `CorBo/validation/acentos_revisao.tsv`, com cada forma, as ocorrências,
a forma alternativa, os lemas e exemplos, e uma coluna `decisao` para preencher. O FORM só muda depois
dessa revisão e quando o `# text` for corrigido, já que o FORM segue o texto.

**[DECIDIR]** Para as alternâncias acima, decidir caso a caso: acentuar a oxítona que está sem acento
(no `# text` e no `FORM`), ou registrar que são palavras diferentes. Decidir também se *pejô* deve
virar *pejó*.

## 5. Maiúsculas e minúsculas

- O `FORM` reproduz a caixa do `# text`. Busca, índices e tokenizador comparam formas sem distinguir
  caixa (`casefold`).
- As frases começam com maiúscula. As exceções são as entradas do dicionário (`dic_`, 950 de 972 em
  minúscula) e cerca de 330 frases de fontes numeradas cujo início foi cortado.
- **Boe/boe (decisão de 22/11/2026).** Aqui a caixa decide a classe: `Boe` é PROPN, lema `Boe`,
  `Number=Plur` ("os Bororo"); `boe` é NOUN, lema `boe`, `Number=Sing`. Em 22/11 foram ajustados 111
  tokens (`scripts/apply_orthography_decisions.py`). A regra vale para as formas exatas *Boe* e *boe*.
  Formas com morfologia (*Boere*, *boeji*…) seguem a anotação de cada uma.

## 6. Pontuação

| Fenômeno | Ocorrência | Convenção atual |
|---|---|---|
| Espaço antes da pontuação (`boe .`) | quase todas as fontes numeradas, `dic_`, Jussila, Adugo Biri | mantido no `# text`; a pontuação é sempre um token próprio |
| Pontuação colada (`boe.`) | *Boe Ero* e parte das fontes numeradas | mantida no `# text`; também vira token próprio |
| Reticências e pontos seguidos (`...`, `..`, `!..`, `.. .`) | cerca de 900 frases | cada token de pontos reproduz o `# text`: pontos colados formam **um** token (`..`, `...`), pontos separados por espaço são tokens distintos (`.. .` = `..` + `.`), e `!..` = `!` + `..` (decisão de 22/11/2026; 408 sentenças ajustadas) |
| Aspas retas `"` | só no *Boe Ero* (55 frases) | mantidas; marcam fala citada |
| Aspas curvas `‘ ’` | 3 frases | mantidas |
| Hífen ou travessão de diálogo (`-Cio`, `- Kaito`) | 35 frases | mantido |
| Hífen silábico (`ko-go-ri-ga`) | canto e fala enfática | mantido dentro da palavra |
| `***` no fim da frase | 3 frases | mantido; provavelmente fim de seção na fonte |
| Número de linha da fonte no início do `# text` | 55 frases (já corrigidas) | vai para `# source_line = N` |

**[DECIDIR]**

1. ~~Tokenização de `..` e `!..`~~: decidido e aplicado em 22/11/2026. Ficam 75 frases em que o
   `# text` tem pontos sem token correspondente (ou o contrário), listadas em
   `CorBo/validation/orthography_fixes_20261122.tsv` (tipo `reticencias_sem_alinhamento`).
2. A função de `***`: marca de fim de seção, que poderia ir para um comentário `# section_end`, ou parte do texto.
3. As aspas do *Boe Ero*: manter, ou registrar a fala citada só pela anotação (`Speech=Quo`).

## 7. Português

O `# text_por` reproduz a tradução ou interpretação da fonte, com a grafia do tradutor. Não é revisado
ortograficamente; só são corrigidos erros de extração (caracteres truncados, quebras de linha).

## 8. Camada normalizada (proposta)

Chave de comparação usada pela busca, pelo painel lexical e pelas estatísticas, calculada nos scripts
e **não** gravada no CoNLL-U:

1. normalização NFC;
2. `casefold` (já implementado);
3. remoção das bordas não alfabéticas (já implementado no painel lexical);
4. **sem** remoção de acentos: o acento marca a oxítona e distingue palavras (seção 4). A busca pode
   oferecer uma opção "ignorar acentos", mas o padrão é respeitá-los.

Quando houver decisão, o painel lexical, `build_corpus_indexes.py` e `corbo-tokenizer` passam a usar a
mesma função de normalização. Hoje cada um tem uma versão própria, todas equivalentes a NFC + `casefold`.

## Resumo das decisões pendentes

| # | Ponto | Seção |
|---|---|---|
| 1 | Letras representadas por U+F063, U+F086, U+F087 no *Boe Ero* | 2 |
| 2 | Tabela grafema–fonema e referência ortográfica | 3 |
| 3 | ~~Acento em palavras Bororo~~: só oxítonas de 2+ sílabas (decidido 22/11); falta revisar `acentos_revisao.tsv` | 4 |
| 4 | ~~Tokenização de `..` e `!..`~~ (aplicado 22/11); 75 frases sem alinhamento | 6 |
| 5 | Função de `***` | 6 |
| 6 | Aspas do *Boe Ero* | 6 |
| 7 | ~~Normalização sem acentos~~: não, o acento é mantido (22/11) | 8 |
