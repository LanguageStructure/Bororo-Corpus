# Convenções ortográficas e de normalização do CorBo

> **Rascunho de 22/11/2026, a revisar por FFG.** O que está aqui descreve o que o corpus **já faz**,
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

A grande maioria das palavras Bororo é escrita **sem acento**. Os diacríticos aparecem em dois contextos.

**Palavras portuguesas** mantêm a grafia do português: *caminhão* (71), *João*, *café*, *você*, *não*.

**Palavras Bororo** recebem às vezes um acento agudo (raramente grave ou circunflexo), quase sempre
na última vogal e alternando com a forma sem acento:

| Sem acento | Com acento |
|---|---|
| ica (47) | icá (30) |
| aro (23) | aró (11) |
| ako (49) | akó (3) |
| kodiba (15) | kodibá (3) |
| ca (227) | cá (8) |
| ta (156) | tá (4) |
| pejo (4) | pejô (4), pejó (2) |
| me (12) | mè (2), mé (1) |
| we (13) | wè (2) |

As formas acentuadas aparecem sobretudo no fim de enunciados de fala direta e de exclamações
(*Akore icá*, *Inagore aró!*), o que sugere marca de ênfase ou de entonação. Isso ainda não foi confirmado.

**[DECIDIR]** Para cada alternância acima, decidir entre duas leituras:

- (a) o acento é **significativo** (ênfase, vocativo, tonicidade): fica em `FORM` e pode ganhar um traço
  em `MISC`, por exemplo `Emph=Yes`;
- (b) o acento é **variação de grafia**: fica em `FORM`, e a camada normalizada o remove.

Hoje a busca e o painel lexical diferenciam maiúsculas de minúsculas apenas para exibição, mas **não
removem acentos**. Por isso *icá* e *ica* aparecem como formas diferentes no léxico e na busca.

## 5. Maiúsculas e minúsculas

- O `FORM` reproduz a caixa do `# text`. Busca, índices e tokenizador comparam formas sem distinguir
  caixa (`casefold`).
- As frases começam com maiúscula. As exceções são as entradas do dicionário (`dic_`, 950 de 972 em
  minúscula) e cerca de 330 frases de fontes numeradas cujo início foi cortado.
- **Boe/boe.** No meio da frase ocorrem as duas grafias: 664 tokens *Boe* e 971 *boe* no total.
  A caixa **não** decide a classe. A classe segue o sentido: etnônimo "os Bororo" = PROPN plural,
  outros sentidos = NOUN singular (decisão de 21/11/2026).

## 6. Pontuação

| Fenômeno | Ocorrência | Convenção atual |
|---|---|---|
| Espaço antes da pontuação (`boe .`) | quase todas as fontes numeradas, `dic_`, Jussila, Adugo Biri | mantido no `# text`; a pontuação é sempre um token próprio |
| Pontuação colada (`boe.`) | *Boe Ero* e parte das fontes numeradas | mantida no `# text`; também vira token próprio |
| Reticências `...` | 426 frases | **um** token `...` (532 tokens) |
| `..`, `!..`, `. .` | cerca de 450 frases | cada ponto vira um token `.` |
| Aspas retas `"` | só no *Boe Ero* (55 frases) | mantidas; marcam fala citada |
| Aspas curvas `‘ ’` | 3 frases | mantidas |
| Hífen ou travessão de diálogo (`-Cio`, `- Kaito`) | 35 frases | mantido |
| Hífen silábico (`ko-go-ri-ga`) | canto e fala enfática | mantido dentro da palavra |
| `***` no fim da frase | 3 frases | mantido; provavelmente fim de seção na fonte |
| Número de linha da fonte no início do `# text` | 55 frases (já corrigidas) | vai para `# source_line = N` |

**[DECIDIR]**

1. Tokenizar `..` e `!..` de forma uniforme: hoje `...` é um token, mas `..` vira dois. Sugestão: toda
   sequência de pontos vira **um** token (`..` → `..`, `!..` → `!` + `..`), sem alterar o `# text`.
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
4. **[DECIDIR, depende do item 4]** remoção de acento agudo, grave e circunflexo nas palavras Bororo,
   mantendo-os nas palavras portuguesas (*caminhão*, *João*). Na prática: remover diacríticos quando o
   token não tem `Lang=pt` nem é PROPN de origem portuguesa.

Quando houver decisão, o painel lexical, `build_corpus_indexes.py` e `corbo-tokenizer` passam a usar a
mesma função de normalização. Hoje cada um tem uma versão própria, todas equivalentes a NFC + `casefold`.

## Resumo das decisões pendentes

| # | Ponto | Seção |
|---|---|---|
| 1 | Letras representadas por U+F063, U+F086, U+F087 no *Boe Ero* | 2 |
| 2 | Tabela grafema–fonema e referência ortográfica | 3 |
| 3 | Acento em palavras Bororo: significativo ou variação gráfica | 4 |
| 4 | Tokenização uniforme de `..` e `!..` | 6 |
| 5 | Função de `***` | 6 |
| 6 | Aspas do *Boe Ero* | 6 |
| 7 | Normalização sem acentos na busca e no léxico | 8 |
