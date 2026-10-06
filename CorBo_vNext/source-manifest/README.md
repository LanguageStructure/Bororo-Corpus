# Archive source triage

This directory records the editorial disposition of the 18 substantive TXT files reviewed from the local Bororo archive.

## Status values

- `imported_staging`: imported into an editorial/documentary staging layer; not automatically counted in the public corpus.
- `partial_import_staging`: only the non-overlapping portion was imported.
- `parallel_witness`: overlaps material already represented in CorBo and is reserved for collation rather than duplicate ingestion.
- `duplicate`: duplicate or near-duplicate of another source; not independently ingested.
- `compilation`: composite source overlapping multiple component witnesses; preserved conceptually as a documentary witness but not ingested wholesale.

## Editorial rule

A source file is not evidence for an additional independent corpus unit merely because it is a separate file. Parallel witnesses are kept separate from public corpus counts until their textual relationship has been reviewed. Source orthography, numbering errors, repetitions, and historical spellings are preserved in the documentary layer; alignments or corrections are recorded in editorial metadata rather than silently normalized.

The manifest describes triage decisions. It does not replace the original source files and does not assert provenance beyond what has been established during review.


## Parallel-witness collation

Parallel witnesses are staged in `CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv` and are not additional public corpus units.

Collation status is deliberately conservative:

- `exact`: normalized Bororo text matches an existing Historia Mítica unit exactly; assigned automatically.
- `candidate`: near-identical textual match (currently >= 0.99); requires human review.
- `confirmed`: a human reviewer has accepted the proposed CorBo correspondence. This status is authoritative and is preserved on later matcher runs.
- `unmatched`: no sufficiently strong automatic correspondence has been established.

Lower-similarity diagnostics and sequence proposals are review aids only. They do not create correspondences automatically. A fuzzy similarity score alone is never treated as documentary equivalence.


### Limits of automatic parallel-witness alignment

Automatic alignment was deliberately calibrated conservatively. After exact and near-exact correspondences were human-reviewed, 309 archival witness units remained unmatched. Additional diagnostics tested rare lexical anchors, ordered sequence gaps, 2–5-unit segmentation windows, and possible component relations.

These diagnostics did not justify further automatic correspondences. In formulaic passages, high lexical or translation similarity can be misleading when a decisive proper name, participant, action, or narrative context differs. Sharing a named person or rare lexical item likewise does not establish unit identity: the same participant may occur in different episodes.

Accordingly:

- `confirmed` is reserved for human-reviewed unit correspondence;
- `component` is reserved for a human-reviewed case where the archival unit is demonstrably represented inside a broader CorBo unit;
- `unmatched` is a valid documentary result and must not be interpreted as an error;
- rare-anchor, fuzzy, sequence, and component scores are diagnostic evidence only;
- no similarity threshold may promote an `unmatched` unit automatically;
- proper names, participants, actions, Portuguese documentary translations, and narrative context take precedence over global string similarity.

The residual unmatched set should therefore be studied as evidence for differences in wording, segmentation, episode selection, and witness structure rather than forced into one-to-one alignment.


## Pemo — Baraedugume: collation result

Sequence-aware review against História Mítica established that this staging document is a parallel witness, not an independent set of public corpus units.

- 83 of 84 editorial units correspond to the História Mítica unit with the same numeric position. The lower-similarity cases were manually inspected; differences are documentary spelling, punctuation, abbreviations, or minor witness variation rather than distinct narrative units.
- `PB.045` is the segmentation exception. Its Bororo text occurs within the final portion of `BOR-CORBO-HM001-u044`; it is therefore a human-reviewed component relation, not a correspondence with `HM001-u045`.
- No Pemo–Baraedugume staging unit is promoted as a new public corpus unit on the basis of this collation.
- The Portuguese fields around HM units 052–053 show an independent alignment problem: their Bororo corresponds to PB 052–053, while the current HM Portuguese text describes other passages. This must be audited separately and does not invalidate the Bororo witness correspondence.


### Pemo — Coqueiro: colação estrutural em andamento

A colação do testemunho `PemoCoqueiro.txt` mostra que ele não deve ser tratado como uma sequência simples de unidades novas. O documento contém material paralelo à História Mítica, repetições internas e segmentação diferente.

Resultados humanos já estabelecidos:

- `PC.184–PC.189` correspondem sequencialmente a `BOR-CORBO-HM001-u146–u151`.
- `PC.224–PC.231` constituem uma segunda versão do mesmo episódio `HM u146–u151`, com segmentação diferente. Em particular, `PC.229–PC.230` expandem material associado ao trecho da rede concentrado na sequência HM, e não devem ser forçados a uma correspondência 1:1 apenas pelo melhor score.
- Scores globais isolados podem ser enganosos: `PC.185–PC.186` tinham melhores matches lexicais fora desse intervalo, mas o contexto narrativo, a tradução portuguesa e a sequência estabelecem `u147–u148`.
- Consequentemente, correspondência sequencial, tradução e contexto narrativo prevalecem sobre similaridade textual isolada.
- `PC.240–PC.242` são um paralelo estrutural de `HM u148–u151`, mas com referentes lexicais distintos (pacas/`apue` e `apueceba` em PC versus o episódio de `cegi/tubore` e `bukerogu` em HM). O trecho é tratado como variante narrativa/formular, não como equivalência unitária 1:1.
- `PC.252–PC.253` correspondem a `HM u176–u177`.
- `PC.255–PC.256` correspondem a `HM u140–u141`.
- `PC.275–PC.276` correspondem a `HM u137–u138`; isso estende para trás a sequência paralela final já ancorada a partir de `PC.276`.
- A revisão retroativa de `PC.257–PC.274` não justifica estender essa equivalência para trás de `PC.275`. `PC.255–PC.262` desenvolvem um episódio de queixadas com arco/flecha, cerco e flechamento; há paralelos formulares com `HM u139–u142`, mas os referentes e a organização narrativa não permitem tratá-lo como duplicata simples.
- `PC.264–PC.273` contêm distribuição das partes da caça entre Ecerae/Tugarege e matador, enumeração anatômica, preparo e carne que fala durante o cozimento. Os melhores scores HM são fragmentários ou semanticamente divergentes; essas unidades permanecem material documental próprio/unmatched até evidência de testemunho equivalente.
- Assim, a fronteira segura do grande paralelo final é atualmente `PC.275`; similaridades anteriores são registradas como paralelos formulares, não como correspondências unitárias.
- `PC.001–PC.041` constituem o primeiro grande arco de Pemo–Coqueiro. `PC.001–PC.019` narram Pemo ensinando Braedugume a falar/nomear e o aparecimento dos *brae*, de seus animais e alimentos; `PC.020–PC.036` afirmam uma origem humana comum, pensamento/saber compartilhados e uma língua inicialmente única, seguida da diferenciação promovida por Pemo; `PC.037–PC.041` contrapõem Bororo e brancos na distribuição de conhecimento/capacidade e fecham com referências a avião e carro. Não há âncoras HM >= 0.70 em `PC.001–PC.039`; `PC.040–PC.041` completam semanticamente o mesmo arco. Assim, `PC.001–PC.183` não apresenta correspondência textual forte com História Mítica nos diagnósticos realizados, embora contenha vários episódios internos coerentes e paralelos temáticos/formulaicos que não devem ser promovidos automaticamente a equivalência documental.\n- `PC.040–PC.041` parecem fechar um episódio anterior sobre Pemo transmitir conhecimento/capacidade, com referências contemporâneas a avião e carro; não são forçados ao episódio seguinte. `PC.042–PC.072` formam o episódio do roubo de Pemo de Braedugume: Jakomea Atugojebado o faz dormir, seus parentes levam Pemo de canoa e Braedugume o recupera por meio do papagaio e do preá. `PC.073–PC.084` formam um arco contínuo de migração e diferenciação linguística: Pemo prepara uma passagem de buriti sobre o rio; durante a travessia, a distância impede que os grupos se entendam, e o relato culmina em Anabo Bororo/Bakurebo Po e nos nomes Barae/Kuiawe versus Bororo. Não há âncoras HM >= 0.70 em `PC.040–PC.079`.\n- `PC.080–PC.084` fecham um episódio anterior com Anabo Bororo, a travessia de Bakurebo Po e a diferenciação das línguas, incluindo os nomes Barae/Kuiawe e Bororo. `PC.085–PC.119` iniciam o arco de Arua Bororo: a arara amarela revela o lugar, segue-se a preparação da aldeia, a chegada e disputa entre os dois homens e, por fim, o som da cabacinha que atrai o povo. Não há âncoras HM >= 0.70. `PC.119` continua diretamente em `PC.120`, quando os atraídos pelo som chegam à beira da praça; portanto `PC.085–PC.136` constituem um arco narrativo contínuo, que termina com Ewidojeba/Uiagudu Maga e a nomeação de Toduio Bororo.\n- `PC.120–PC.136` preservam o episódio de Ewidojeba/Uiagudu Maga: distinção entre Bororo com e sem enfeites, intervenção do irmão compassivo e estabelecimento/nomeação de Toduio Bororo. Não há âncoras HM >= 0.70. `PC.137–PC.159` iniciam o episódio de Jerigi Otojiwu após a grande inundação: reconstrução da casa, inspiração não reconhecida de Pemo e aprendizado do assobio que chama os Bororo. `PC.159` termina com o assobio “Barogwa kododu” e continua diretamente em `PC.160`, onde se espera e se recebe a resposta; por isso `PC.137–PC.183` são tratados como um único arco narrativo contínuo e documentalmente próprio.\n- `PC.160–PC.183` também formam material narrativo próprio: assobios e fogo no pátio precedem o aparecimento progressivo das casas, do *baito* e dos Bororo; `PC.176` nomeia Turugudu Pijiwu como o primeiro a chegar, e `PC.179–PC.183` levam à chegada dos demais, mudança e novo acampamento. Não há âncoras HM >= 0.70. `PC.183` prepara a saída para caçar e `PC.184` inicia o episódio que passa a corresponder a `HM u146–u151`; assim, a fronteira textual segura do paralelo é `PC.184`, não antes. A ausência de `PC.178` é preservada como lacuna de ID editorial (resultado de merge/importação), não preenchida nem renumerada.\n- `PC.190–PC.223` formam um bloco narrativo coerente sem âncoras HM >= 0.70 no diagnóstico global/janelas. A revisão semântica distingue: (i) `PC.190–199`, retorno com os lambaris, desaparecimento da rede e explicação de que Pemo conduziu a descoberta; (ii) `PC.200–208`, experiência paralela das mulheres com cará e a provisão recorrente de alimento por Pemo; (iii) `PC.209–223`, nova mudança de acampamento e Jokugo orientando os Bororo, embora seu pensamento/sabedoria procedam de Pemo. Na ausência de testemunho equivalente identificado, o bloco é preservado como material documental próprio e não recebe `corbo_match_id` por similaridade formular.

O bloco final a partir de `PC.276` possui uma extensa sequência paralela à História Mítica; a colação dos blocos anteriores continua antes de qualquer promoção de material ao corpus público.


### Pemo–Coqueiro: collation status

The Pemo–Coqueiro witness is collated through all 330 editorial units. Persistent decisions are generated by `scripts/build_pemo_coqueiro_collation.py` into `CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_collation.tsv`.

Decision semantics:
- `unique`: no textual HM equivalent was identified in the completed collation; this is not yet automatic authorization for public-corpus ingestion.
- `confirmed`: human-reviewed documentary correspondence to a specific CorBo/HM unit.
- `parallel_formulaic`: narrative, structural, formulaic, or segmentation parallel without sufficient evidence for strict 1:1 documentary equivalence.
- `unresolved`: reserved for cases still requiring human collation; the completed review should currently yield zero such rows.

The collation layer is deliberately separate from `source` and `reviewed`: documentary text remains unchanged, and collation decisions do not constitute orthographic/editorial normalization.


## Archive additions: public-corpus audit

The 226 units in `archive_additions_editorial.tsv` were audited against the complete public CorBo after Pemo–Coqueiro integration (9,737 units). No exact match and no near-exact match at >= 0.99 was found. A broader candidate review at >= 0.55 produced 36 isolated candidates, mostly formulaic/noisy. A sequence diagnostic found only two apparent monotonic pairs, both in Primeiras Andanças: PAND.060–061 vs. Coqueiro S08 p030–031 and PAND.061–062 vs. Pemo–Coqueiro PC.271/274. Human review of the surrounding Bororo and Portuguese context rejected both as documentary equivalences: the Coqueiro passage concerns cattle, a non-Indigenous man, horse, food and coffee; PC.271–274 concerns cooking peccary meat and the beginning of a new search, whereas PAND.060–064 concerns the caracara hawk/“spirit” and Birimodo's hunting party. Thus all 226 archive-addition units remain without an identified public-corpus duplicate. This is an ingestion decision, not orthographic normalization; source text remains unchanged.
