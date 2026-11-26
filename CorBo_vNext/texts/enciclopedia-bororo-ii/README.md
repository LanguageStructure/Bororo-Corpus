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
- Sem hífens e sem apóstrofos no texto paralelo; *-u* depois de vogal = sufixo *-wu*, também antes de sufixo (*Kujagureu* → *Kujagurewu*; *Kurireu-re* → *Kurirewure*). Só depois de *a*, *e*, *o*: *kakodiu* (lenda 5), palavra própria da língua das lendas, fica como impressa.
- Hífens de formas bororo também saem dos títulos e dos textos em português (traduções, narrativa, notas, glosas):
  *Kaiamo-doge* → *Kaiamodoge*, *KAIAMO-DOGE JI-WU BAKARU* → *KAIAMODOGE JIWU BAKARU*. Os hífens do português ficam
  (*cipó-imbé*, *atiraram-se*, *cana-de-vassoura*). A transcrição guarda a forma impressa.
- *nure* e *rogu* se escrevem ligados à palavra anterior (*Boe nure* → *Boenure*; *nogedu rogu* → *nogedurogu*). No interlinear, a célula ligada tem `ligada=1`; no leitor, as glosas aparecem juntas ("menino + (com) pequenez").
- Nomes bororo dentro do português sem diacríticos (Meriri Poro). Português na ortografia original (êle, fêz).
- Erros de impressão mantidos (ex.: "aldeia cm"), salvo o hífen entre nome e sobrenome em *Aroia-Kurireu-ji* (lenda 2, frase 45), transcrito *Aroia Kurireu-ji* para não juntar os nomes.
- As notas citam as formas bororo como impressas (com hífens, sem diacríticos).

## Estado

- Lenda 1, *A grande inundação* (pp. 3–23): 65 frases (1–41 texto principal; 42–50 variante 1; 51–65 variante 2),
  38 notas.
- Lenda 2, *Os chefes Baitogogo e Aroia Kurireu lutam contra os Kaiamo-doge* (pp. 25–77; abre o ciclo do chefe
  Baitogogo): 181 frases, 70 notas. As notas 1 e 36 não têm chamada impressa no texto bororo. Divergências do
  original mantidas: nota 16 (*čáči*) × texto (*čái*); nota 40 (*kajéje*) × texto (*bukéje*); *ičái* (frases 57, 95, 138).
- Lenda 3, *Os chefes Baitogogo e Aroia Kurireu embelezam os rios* (pp. 79–89): completa, 19 frases e 13 notas
  (pp. 85–86 transcritas de fotos enviadas por FFG).
- Lenda 4, *O chefe Baitogogo batiza o morro Kudorori* (pp. 91–109): completa, 85 frases (variante 65–85) e
  70 notas; pp. 99–102 transcritas de fotos enviadas por FFG. A nota 55 não tem chamada impressa.
- Lenda 5, *O chefe Baitogogo e as flechas* (pp. 111–117): completa, 15 frases e 17 notas (pp. 111–112 de fotos).
- Transcrição provisória, a conferir por FFG.
