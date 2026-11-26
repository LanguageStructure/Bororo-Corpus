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
- Sem hífens e sem apóstrofos no texto paralelo; *-u* depois de vogal = sufixo *-wu*, também antes de sufixo (*kurireu-re* → *kurirewure*; *ekureu-ge* → *ekurewuge*). Só depois de *a*, *e*, *o*: *kakodiu* (lenda 5), palavra própria da língua das lendas, fica como impressa. Ideofones (*peu*, *cou*, *pou*) ficam sem *-wu*.
- Nomes próprios ficam como impressos, sem *-wu* (FFG, 26/11/2026): *Aroia Kurireu-re* → *Aroia Kurireure*, *Jakomea Kujagureu*, *Eigawa Enawureu*, *Pogubo Cereu*. Critério do script: palavra com maiúscula inicial que não abre frase, citação ou período. Assim *Aipobureu*, *Ipocereu* e *Pobogoreu-ge* com maiúscula (personagens da lenda 9) ficam como impressos, e *aipobureu* com minúscula (lista de animais) recebe *-wu* (confirmado por FFG).
- Contrações com apóstrofo que se desfazem (FFG, 26/11/2026): *Adugo-dog'ei* → *Adugodoge ei*; *Adugo-dog'ebo* → *Adugodoge ebo*; *Korog'ebo* → *Koroge ebo*; *arem'ei* → *areme ei*; *Bo'ei* → *Boe ji* (*Bo'ei-boe* → *Boe ji boe*). Generalizado a consoante + *'ei*/*'ebo* (*kugur'ei* → *kugure ei*; *batarareu-g'ei* → *batararewuge ei*; *pa-dugareg'ei* → *padugarege ei*). Vogal + *'ei*: *ki'ei* → *kie ei*; *Aro'ei* → *Aroe ji*, como *Boe ji*; *Aroro'e'bo* → *Aroroe ebo*, como *ime ebo*.
- *i-aidu-re* → *itaidure*; *i-aidu-ka-re* → *itaidukare* (FFG, 26/11/2026; como no CorBo).
- Hífens de formas bororo também saem dos títulos e dos textos em português (traduções, narrativa, notas, glosas):
  *Kaiamo-doge* → *Kaiamodoge*, *KAIAMO-DOGE JI-WU BAKARU* → *KAIAMODOGE JIWU BAKARU*. Os hífens do português ficam
  (*cipó-imbé*, *atiraram-se*, *cana-de-vassoura*). A transcrição guarda a forma impressa.
- Formas contraídas que se separam (tabela `SPLIT` no script): *ime'bo*/*im'e'bo* → *ime ebo*; *ipare'bo*/*ipar'e'bo* →
  *ipare ebo*; *mano-to* → *mano to*.
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
- Lenda 6, *O chefe Baitogogo apodera-se do espírito Aije* (pp. 119–125): completa, 14 frases e 22 notas.
- Lenda 7, *Os chefes Baitogogo e Akaruio Boroge cedem seus poderes* (pp. 127–137): completa, 21 frases e 38 notas
  (a nota 2 não tem chamada impressa). O ideofone *peu* (som do tambor) fica sem *-wu*.
- Lenda 8, *Os chefes Baitogogo e Akaruio Boroge vão chefiar o reino dos mortos* (narrativa pp. 139–142; texto bororo
  pp. 144–182, do arquivo *cut-2.pdf*; p. 143 só com ilustrações; p. 183, com a tradução das frases 168–170 e as
  notas 86–89, do arquivo *cut-3.pdf*): completa, 170 frases e 89 notas. A nota 89 não tem chamada impressa.
  Ideofones *cou* e *peu* sem *-wu*.
- Lenda 9, *Os gêmeos Akaruio Bokodori e Mamuiawuge Eceba* (abre o ciclo do chefe Akaruio Bokodori, p. 185;
  introdução e narrativa pp. 187–191; texto bororo *Bakororo-doge e-ro* pp. 192–255, seções a–k, do arquivo
  *cut-3.pdf*): completa, 217 frases e 112 notas. Divergências do original mantidas:
  - notas 71, 72 e 97 sem chamada própria: a chamada da frase 141 (*podoja-to*) está impressa como (70), a da frase
    192 (primeiro *taci*) como (96), e a frase 142 (*to-iado apo*) não traz chamada;
  - p. 238, frase 158: a última célula traz só as glosas "fará" / "ao.", sem forma bororo (registrado como lacuna);
  - frase 70 *ino* (nas frases paralelas: *oino*); frase 84 *bukeje* (letra inicial falhada na impressão);
    frase 124 *ae* (impresso *ác*); frase 173 célula *u-re* com glosa "sôbre"; frase 22 *i-vidodu* (com *v*);
  - *apekura arege* (frases 94 e 180) × *Apegura Arege* (frases 126 e 128);
  - erros da tradução portuguesa mantidos: "(de) sua) viagem" (26), parêntese aberto em 125, "supergície" (84),
    "palvra" (128), "tue ôlho" (207); glosa "(sou) em mesmo" (55).
  - O ideofone *pou* (pancada) fica sem *-wu*, como *peu* e *cou*.
- Lenda 10, *O chefe Akaruio Bokodori e as tabas bororo* (pp. 257–261): completa, 14 frases e 15 notas.
- Lenda 11, *O chefe Akaruio Bokodori e as onças* (pp. 263–267): completa, 10 frases e 13 notas. Na frase 4 a
  célula *po-to.* tem a glosa "(da) água" (impresso assim).
- Lenda 12, *O chefe Jerigi Otojiwu derrota a tribo dos Koroge* (abre o ciclo do chefe Jerigi Otojiwu; pp. 271–287;
  p. 286 com o fim do texto bororo e metade em branco): completa, 55 frases e 28 notas. Divergências mantidas:
  introdução *Jerigo Otojiwu* e narrativa *Jerigi Otowu* (sic); frase 13 "três" = *pobe ma jewu metuia bokware*
  numa só célula.
- Lenda 13, *O chefe Jerigi Otojiwu generaliza um costume do clã dos Bokodori Ecerae* (pp. 289–299; p. 291 em
  branco): completa, 24 frases e 15 notas. A nota 3 é chamada duas vezes (frases 2 e 10) e a nota 8 duas vezes na
  frase 14, como no original. *Ao Kureuge* e *Kumo-doge* ficam como impressos (sem hífen antes de *-ge*, a regra
  -wu não se aplica); narrativa "travalhavam" e "coupana" (sic).
- Transcrição provisória, a conferir por FFG.
