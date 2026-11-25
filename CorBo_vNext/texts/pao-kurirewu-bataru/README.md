# Pao Kurirewu Bataru Kurirewu — fonte

Novo Testamento em língua Bororo, segunda tradução do NT no CorBo (a primeira é o *Bakaru Maiwu*,
Ochoa Camargo 1992, em `../bakaru-maiwu/`).

**Referência:** *Pao Kurirewu Bataru Kurirewu: O Novo Testamento na língua Borôro do Brasil*.
Tradução © 2019, Wycliffe Bible Translators, Inc.

**Licença deste diretório:** [Creative Commons Atribuição-NãoComercial-SemDerivações 4.0
(CC BY-NC-ND 4.0)](https://creativecommons.org/licenses/by-nc-nd/4.0/), como indicado na fonte. Esta licença
é **diferente** da CC BY 4.0 do restante do CorBo (ver `LICENSE` na raiz, "salvo indicação específica em
contrário em um arquivo ou diretório"). O texto não pode ser usado para fins comerciais.

**Ortografia:** adaptada por Fabrício Ferraz Gerardi à ortografia usada no CorBo e na gramática do Bororo em
preparação. O texto não tem outras alterações.

## Arquivos

- `source/NT_SIL.txt`: texto completo com a ortografia adaptada, como recebido (cabeçalho com os metadados nas
  primeiras linhas).
- `<livro>/<livro>.tsv`: um arquivo por livro, gerado por `scripts/import_pao_kurirewu_bataru.py`, com as mesmas
  colunas do *Bakaru Maiwu* (`id, book, book_code, chapter, verse, source, reviewed, editorial_note`).
  - Uma linha por versículo; quando a fonte junta versículos, a linha cobre a faixa (`verse` = `7-8`, ID
    `…-005-007_008`).
  - Títulos de seção da fonte: linhas sem `verse`, ID `…-HEAD-NNN`.
  - IDs: `BOR-CORBO-PKB-<livro>-<capítulo>-<versículo>`, com os códigos de livro do *Bakaru Maiwu* (MAT, MRK…).

Para gerar de novo: `python scripts/import_pao_kurirewu_bataru.py` (simula) e depois `--apply`. As anomalias
de numeração vão para `CorBo/validation/pao_kurirewu_bataru_import.tsv` (coluna `decisao`).

## Observações da importação (25/11/2026)

- 7.458 unidades de versículo (380 faixas) e 823 títulos de seção; 7.947 versículos cobertos.
- **Mateus 1:12–23 falta na fonte**: o texto passa do v. 11 para o fim do v. 23 ("(Nou boe egore “Emanuel”…)")
  e segue no v. 24. O trecho ficou no v. 11 até que a fonte seja completada.
- Em 21 capítulos o texto antes do primeiro número cobre mais de um versículo (ex.: Mt 7:1–2, Lc 1:1–4); a
  faixa foi inferida e registrada em `editorial_note`.
- Sete títulos de seção caem no meio de um versículo (ex.: Mc 6:6, Jo 18:38); o título aparece depois do versículo.
- O Apocalipse não tem linha com o nome do livro na fonte; foi identificado pela posição (depois de Judas).
- O título "Hebrewus" da fonte corresponde a Hebreus.
- Numerais do texto (40, 25 mil, 60…) não são tratados como versículos; estão listados no relatório.
