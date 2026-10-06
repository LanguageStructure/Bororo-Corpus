# Convenção de anotação morfológica do CorBo

Esta nota define a representação mínima usada pelo CorBo para que evidência morfológica possa ser recuperada no nível do token sem inferir segmentações a partir da forma gráfica.

## Princípios

1. A forma documental do token permanece em `FORM`. A ortografia da fonte não deve ser alterada para acomodar a análise.
2. Segmentação morfêmica só conta como evidência explícita quando está registrada na própria anotação.
3. O índice público não deve reconstruir morfemas automaticamente por semelhança gráfica.
4. A segmentação e a interpretação gramatical são camadas distintas: uma fronteira pode ser segura mesmo quando a função de um morfema ainda é provisória.
5. Ausência de segmentação explícita significa apenas “não segmentado nesta camada”, não “morfologicamente simples”.

## MISC

A partir desta convenção, a segmentação explícita deve ser registrada em `MISC` no campo `MORPH`. O build ainda aceita `GLOSS` como campo legado quando ele contém fronteiras explícitas, para preservar compatibilidade com anotações existentes.

Convenção de fronteiras:

- `-` = fronteira afixal;
- `=` = fronteira clítica.

Exemplos estruturais:

```text
MORPH=i-nu-re|GLOSS=1SG-PROG-IND
MORPH=ce=FORMA|GLOSS=1PL.EX=...
MORPH=FORMA=iagu|GLOSS=...=QUO
```

`MORPH` contém os segmentos; `GLOSS` contém as glosas alinhadas na mesma ordem. Esses exemplos ilustram a estrutura de codificação e não substituem a análise linguística validada de cada forma.

Campos como `ORTHO`, `POS_FINE`, `CLS` e `PRCLITIC` podem continuar em `MISC` quando necessários, mas não substituem a segmentação explícita.

## FEATS

`FEATS` registra propriedades gramaticais do token segundo a convenção adotada no projeto. Não deve ser usado como substituto genérico de uma segmentação morfêmica.

Uma exceção documental já utilizada pelo CorBo é `Speech=Quo`: quando uma forma termina em `iagu`, essa anotação licencia a evidência token-level de `-iagu`. O índice registra explicitamente que a fonte dessa evidência é `FEATS:Speech=Quo`.

## Evidência pública

O build gera `docs/data/morpheme-tokens.json`. Cada registro deve poder ser rastreado até:

- `sent_id`;
- ID do token;
- forma;
- segmentação explícita, quando houver;
- lema e categorias disponíveis;
- sentença e tradução;
- fonte da evidência (`MISC/MORPH`, `MISC/GLOSS` legado ou uma regra explícita documentada).

O arquivo não deve conter segmentações produzidas por heurística sobre `FORM`.

## Busca

A interface distingue:

- **evidência token-level**: análise explicitamente recuperável do CoNLL-U;
- **forma associada ao morfema**: projeção documental baseada em uma forma já relacionada ao morfema.

A segunda categoria serve para concordância e descoberta no corpus, mas não deve ser apresentada como nova anotação morfológica dos tokens encontrados.

## Revisão

Novas regras especiais de extração devem ser documentadas antes de entrarem no build. Morfemas ou funções cuja análise ainda não esteja consolidada podem permanecer provisórios; isso não autoriza normalização automática da fonte documental.
