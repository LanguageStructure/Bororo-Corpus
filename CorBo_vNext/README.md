# CorBo vNext

This directory is a non-destructive staging area for the reorganization of the Bororo documentary corpus (CorBo).

## Scope

CorBo vNext contains documentary and textual corpus data. The Universal Dependencies treebank and other syntactic annotation are intentionally kept outside this structure.

The editorial pipeline is:

`source → curated text/source units → parallel alignment → derived/search layers`

Source wording and orthography are preserved. Normalized forms, when eventually supplied, must be stored as a separate layer and must never silently overwrite a source witness.

## Proposed structure

- `metadata/` — collection- and text-level metadata and manifests.
- `texts/` — curated documentary texts, grouped by collection/work/witness.
- `parallel/` — Bororo–Portuguese alignments with explicit alignment status.
- `sources/` — provenance records and source inventories; source binaries remain untouched until rights and repository-size decisions are made.
- `schema/` — field definitions, identifiers, genre vocabulary, and editorial conventions.

## Stable identifiers

Corpus text identifiers use the prefix `BOR-CORBO-`. Source units receive IDs derived from the text ID. A source unit is not automatically equivalent to a linguistic sentence: narratives, songs, ritual performances, lists, and documentary notes may require different segmentation units.

## Collections already under editorial preparation

- Roia Kurireu
- Ekeroia
- Oieigo
- História Mítica
- Bakarudoge / Frederico Coqueiro
- Kleber–Tiago materials
- Coqueiro Bororo–Portuguese compilation

The Coqueiro compilation currently has a section-aware alignment workflow. Candidate pairs are separated from structurally verified pairs; `verified_structural` describes documentary alignment confidence, not linguistic or translation validation.

## Status

This directory is being developed on a dedicated restructuring branch. Existing `CorBo/` and `Tagged_CorBo/` data on `main` are not modified or deleted during this stage.
