# Ética, consentimento e governança dos dados

> **Estado: modelo a preencher.** Este documento foi estruturado para o CorBo, mas
> **nenhuma informação factual foi presumida**. Todos os trechos entre
> **[A PREENCHER: …]** dependem de informações que só o responsável pelo projeto
> (e, quando for o caso, a comunidade Boe) pode fornecer. Até ser preenchido, não
> deve ser citado como declaração do projeto.

## 1. A língua e a comunidade

O Boe-Bororo (ISO 639-3 `bor`) é falado pelo povo Boe em Mato Grosso, Brasil. O CorBo é desenvolvido no âmbito da iniciativa **Boe eno moto**.

- Relação do projeto com as comunidades e organizações Boe: **[A PREENCHER: aldeias/Terras Indígenas envolvidas, associações, lideranças, escolas]**
- Papel de falantes e professores Boe no projeto (consultores, coautores, revisores, transcritores): **[A PREENCHER]**
- Como a comunidade é informada sobre o uso e a publicação dos dados: **[A PREENCHER]**

## 2. Origem dos materiais e base de publicação

A coluna "O que o repositório registra" foi preenchida a partir de `CorBo_vNext/metadata/collections.tsv`, `CorBo_vNext/source-manifest/` e do README; as demais colunas dependem do responsável pelo projeto.

| Material | O que o repositório registra | Base para publicação | Restrições |
|---|---|---|---|
| Bakarudoge | coleção narrativa; Frederico Coqueiro; Meruri; ca. 1982–1984 | **[A PREENCHER]** | **[A PREENCHER]** |
| Coqueiro | compilação Bororo–Português autobiográfica/histórica, 34 seções (`CorBo/Corpus_Files/biografia/`) | **[A PREENCHER]** | **[A PREENCHER]** |
| Boe Ero – *Vida Bororo* | obra publicada; 8 textos, 276 registros paralelos | **[A PREENCHER: autorização dos titulares / uso acadêmico]** | **[A PREENCHER]** |
| História Mítica, Adugo Biri, Marigudu, Kleber–Tiago | textos narrativos e de discurso, com testemunhos paralelos | **[A PREENCHER]** | **[A PREENCHER]** |
| Materiais de arquivo (Pemo–Coqueiro, Archive additions, Archive parallel witnesses) | 18 arquivos TXT de um arquivo Bororo local, triados em `archive_source_triage.tsv` | **[A PREENCHER: acervo de origem, autorização ou domínio público]** | **[A PREENCHER]** |
| Textos bíblicos e Bakaru Maiwu (NT) | arquivos `*_2-orthophon.txt` em `CorBo/Corpus_Files/bíblia/` | **[A PREENCHER: titular dos direitos e autorização]** | **[A PREENCHER]** |
| Cantos rituais: Roia Kurirewu, Ekeroia, Oieigo | Ekeroia: 627 cantos preparados, **publicação retida** até revisão humana | **[A PREENCHER]** | **[A PREENCHER: há cantos de circulação restrita?]** |
| Etnobotânica e fauna | vocabulário temático só publica entradas expressamente autorizadas, com planilha fora do repositório (`docs/VOCABULARIO_TEMATICO.md`) | **[A PREENCHER]** | conforme autorização por entrada |
| Sentenças anotadas sem coleção identificada (10.554 com ID numérico, 971 `dic_`, 52 `Jussila`) | origem não registrada no repositório (ver `CorBo/validation/sent_id_groups.tsv`) | **[A PREENCHER]** | **[A PREENCHER]** |

## 3. Consentimento

- Procedimento de consentimento usado no trabalho de campo: **[A PREENCHER: oral/escrito, idioma, quem registrou, onde está arquivado]**
- Aprovação ética institucional, se houver (comitê, número do parecer, instituição): **[A PREENCHER ou "não se aplica", com justificativa]**
- Autorizações de órgãos competentes, se aplicável: **[A PREENCHER]**
- Identificação de falantes: **[A PREENCHER: nomes publicados com autorização / pseudônimos / anonimização]**
- Como um falante ou a comunidade pode pedir retirada ou restrição de um material: **[A PREENCHER: contato e procedimento]**

## 4. Princípios de governança

O projeto se orienta por:

- **FAIR** — dados localizáveis, acessíveis, interoperáveis e reutilizáveis: DOI por versão no Zenodo, formato CoNLL-U, metadados e licença explícitos;
- **CARE** (Global Indigenous Data Alliance) — *Collective benefit*, *Authority to control*, *Responsibility*, *Ethics*. Como o projeto os aplica: **[A PREENCHER: p. ex. retorno de materiais às escolas, decisões de publicação tomadas com a comunidade, uso didático]**.

Práticas já adotadas no repositório:

- a fonte documental não é alterada; correções e análises ficam em camadas separadas;
- o vocabulário temático só é publicado com autorização expressa por entrada, a partir de planilha mantida fora do repositório;
- coleções com revisão humana pendente (ex.: Ekeroia) não são publicadas;
- o gerador experimental não produz Bororo livremente: só realiza combinações licenciadas por análise humana.

## 5. Licença e usos

Dados e conteúdos sob **CC BY-NC-SA 4.0**, salvo indicação específica. **[A PREENCHER: a comunidade foi consultada sobre a licença? Há itens com licença diferente ou acesso restrito? Usos que o projeto pede que não sejam feitos, p. ex. treinamento de modelos comerciais, uso de cantos fora de contexto.]**

## 6. Créditos

**[A PREENCHER: falantes, consultores, transcritores e tradutores a creditar, com a forma de crédito que cada um autorizou.]**

## 7. Contato

**[A PREENCHER: e-mail para dúvidas, correções e pedidos de retirada.]**
