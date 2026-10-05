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

O bloco final a partir de `PC.276` possui uma extensa sequência paralela à História Mítica; a colação dos blocos anteriores continua antes de qualquer promoção de material ao corpus público.
