# CorBo v0.10.1 — notas de lançamento

**Data:** 25 de novembro de 2026 · **DOI desta versão:** [10.5281/zenodo.24530404](https://doi.org/10.5281/zenodo.24530404) · **Licença:** CC BY 4.0, com exceção para o
*Pao Kurirewu Bataru Kurirewu* (CC BY-NC-ND 4.0) · **DOI de todas as versões:** [10.5281/zenodo.12110451](https://doi.org/10.5281/zenodo.12110451)

## Em números

| | v0.10.0 | v0.10.1 |
|---|---:|---:|
| Unidades do corpus documental (site) | 11.207 | 19.488 |
| Tokens do corpus documental | 262.209 | 539.117 |
| Formas distintas | 17.756 | 21.024 |
| Corpus documental sem textos bíblicos | — | 2.374 unidades · 85.753 tokens |
| Unidades no CoNLL-U | 12.020 | 12.020 |
| Tokens no CoNLL-U | 79.521 | 79.521 |
| Sentenças gold | 1.900 | 1.900 |
| Erros de validação | 706 | 706 |

O corpus documental e a camada anotada são contados separadamente; o crescimento desta versão está todo no
corpus documental (os dois Novos Testamentos não têm anotação CoNLL-U).

## Principais mudanças

- **Segunda tradução do Novo Testamento:** *Pao Kurirewu Bataru Kurirewu* (© 2019 Wycliffe Bible Translators), com
  a ortografia adaptada à do CorBo por Fabrício Ferraz Gerardi. 7.458 unidades de versículo e 823 títulos de seção.
- **Comparação paralela** (`novo-testamento-paralelo.html`): *Bakaru Maiwu* e *Pao Kurirewu Bataru Kurirewu* lado a
  lado, alinhados por versículo.
- **Estatísticas com recorte:** formas, n-grams e diversidade lexical com ou sem os textos bíblicos, que são cerca de
  84% dos tokens.
- **Causativas** com um só `nsubj` por verbo (causado `iobj:agent`/`obl:agent`) e **bito** como verbo transitivo.
- **Língua e metadados:** nome *Boe Ewadaru*; família Bororo, sem Macro-Jê.
- **Integração contínua:** o fluxo que gera os índices do site voltou a funcionar.

## Licença

O CorBo continua sob CC BY 4.0. A exceção é o diretório `CorBo_vNext/texts/pao-kurirewu-bataru/` e os dados
derivados dele (`docs/data/pao-kurirewu-bataru-units.json`, `docs/data/nt-parallel/`,
`docs/downloads/pao-kurirewu-bataru.tsv`), que seguem a licença da fonte, CC BY-NC-ND 4.0 (uso não comercial).

## Limitações conhecidas

- *Pao Kurirewu Bataru Kurirewu*: Mateus 1:12–23 falta na fonte; as anomalias de numeração estão em
  `CorBo/validation/pao_kurirewu_bataru_import.tsv`.
- A numeração de versículos do *Bakaru Maiwu* vem da transcrição e tem lacunas.
- Traduções `# text_por` em parte desalinhadas; camada silver automática; 706 erros de validação listados.
