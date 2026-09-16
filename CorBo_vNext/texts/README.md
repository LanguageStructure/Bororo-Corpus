# CorBo documentary texts

This directory contains documentary text collections prepared for the next CorBo structure.

## Principles

- Documentary corpus data are kept separate from UD/treebank annotation.
- Source transcription is preserved and is not silently normalized.
- Reviewed orthography is stored as a derived layer when available.
- Parallel Bororo–Portuguese data are retained when alignment is supported by the source.
- Ritual songs, verses and other non-prose material are not forced into sentence segmentation.
- Stable corpus IDs link source, reviewed and parallel representations.

## Collections being integrated

- `coqueiro/` — Frederico Coqueiro material; Bororo-only and Bororo–Portuguese parallel views.
- `roia-kurireu/` — numbered Roia Kurireu text and Portuguese translation where present.
- `oieigo/` — multiple witnesses/instances of the Oieigo tradition.
- `ekeroia/` — Ekeroia sets with source text and interpretive material kept distinct.
- `bakarudoge/` — Bakarudoge texts; parallel units only where same-number alignment is structurally supported.
- `kleber-tiago/` — Tiago and Kleber source materials retained as independent documentary records.

The files in this branch are a non-destructive restructuring layer. Existing CorBo data remain untouched until the new organization is validated.