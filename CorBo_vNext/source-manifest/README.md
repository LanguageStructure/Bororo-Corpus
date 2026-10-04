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
