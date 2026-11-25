# Enciclopédia Bororo, vol. II — Lendas

Fonte: ALBISETTI, César; VENTURELLI, Ângelo Jayme. *Enciclopédia Bororo*, vol. II: *Lendas e antropônimos*.
Campo Grande: Museu Regional Dom Bosco, 1969. (Dados bibliográficos a conferir.)

Cada lenda da Enciclopédia tem: introdução; narrativa em português; variantes em prosa; texto bororo interlinear
em frases numeradas (bororo em cima, glosa palavra por palavra embaixo); tradução numerada; notas de rodapé;
legendas de ilustrações.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `transcricao/lendaNN.txt` | transcrição marcada, feita a partir das imagens das páginas (fonte desta coleção) |
| `enciclopedia_ii_parallel.tsv` | uma linha por frase: `source` (forma impressa), `bororo` (ortografia do CorBo), `portuguese` (tradução numerada) |
| `enciclopedia_ii_lendaNN_paralelo.txt` | texto paralelo simples, linha bororo / linha portuguesa |
| `enciclopedia_ii_interlinear.tsv` | células do interlinear: forma impressa, forma normalizada, glosa, nota |
| `enciclopedia_ii_notas.tsv` | notas, com as frases que as chamam |
| `enciclopedia_ii_editorial.tsv` | introdução, narrativa, variantes, cabeçalhos de seção, legendas |
| `enciclopedia_ii_normalizacao.tsv` | forma normalizada × impressa, ocorrências, se já é atestada no CorBo |

Todas as tabelas são geradas por `python scripts/build_enciclopedia_ii.py` (use `--check` para só conferir).
Não as edite à mão: corrija a transcrição e gere de novo.

## Convenções (decisões de FFG, 25/11/2026)

- Bororo sem acentos e sem diacríticos subscritos (ẹ ọ ụ → e o u; k̲ d̲ t̲ → k d t; č → c; ǰ → j).
- Texto paralelo = frase bororo + tradução numerada da Enciclopédia (não as glosas).
- Sem hífens e sem apóstrofos no texto paralelo; *-u* depois de vogal = sufixo *-wu* (*Kujagureu* → *Kujagurewu*).
- *nure* e *rogu* se escrevem ligados à palavra anterior (*Boe nure* → *Boenure*; *nogedu rogu* → *nogedurogu*). No interlinear, a célula ligada tem `ligada=1`; no leitor, as glosas aparecem juntas ("menino + (com) pequenez").
- Nomes bororo dentro do português sem diacríticos (Meriri Poro). Português na ortografia original (êle, fêz).
- Erros de impressão mantidos (ex.: "aldeia cm").
- As notas citam as formas bororo como impressas (com hífens, sem diacríticos).

## Estado

- Lenda 1, *A grande inundação* (pp. 3–23): 65 frases (1–41 texto principal; 42–50 variante 1; 51–65 variante 2),
  38 notas.
- Lenda 2, *Os chefes Baitogogo e Aroia Kurireu lutam contra os Kaiamo-doge* (pp. 25–77; abre o ciclo do chefe
  Baitogogo): 181 frases, 70 notas. As notas 1 e 36 não têm chamada impressa no texto bororo. Divergências do
  original mantidas: nota 16 (*čáči*) × texto (*čái*); nota 40 (*kajéje*) × texto (*bukéje*); *ičái* (frases 57, 95, 138).
- Transcrição provisória, a conferir por FFG.
