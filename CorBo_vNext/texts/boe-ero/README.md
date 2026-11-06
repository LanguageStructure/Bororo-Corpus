# Boe Ero Vida Bororo

This directory preserves the documentary Bororo–Portuguese alignment from the source file `BOE ERO  - VIDA BORORO(1).docx` and keeps later editorial work in separate fields.

## Provenance

- Documentary title: `BOE ERO` / `VIDA BORORO`
- Source credit: `Texto escolar documentado pelo Mestre Mario Bordiognon Enaureu`
- Source SHA-256: `950ed51dfe9b7dcfac3076d44a3b39592d5779a37f26e3b0f7c21cb13c86b8f3`
- Structure: 8 texts, 276 parallel records, 275 records with Bororo source text
- Speakers and translators: preserved per record in `boe_ero_parallel.tsv`

The source binary is not committed here. CorBo vNext keeps source binaries outside version control until rights and repository-size decisions are settled; the filename and digest identify the exact witness used for this extraction.

## Files

- `boe_ero_parallel.tsv` is the canonical documentary and editorial table. `source` preserves the extracted Bororo witness; `reviewed` is a separate human-editable layer. Existing reviewed values must not be replaced by regeneration.
- `boe_ero_unannotated.conllu` is a standalone annotation file generated from the current displayed Bororo text (`reviewed` when present, otherwise `source`). It is not merged into `CorBo/Corpus_Files/CorBo.conllu` and is not gold annotation.
- `boe_ero_alignment_issues.tsv` records source numbering, alignment, and character-encoding anomalies without silently repairing the witness.

Regenerate or verify the derived website JSON and standalone CoNLL-U with:

```bash
python3 scripts/build_boe_ero_assets.py
python3 scripts/build_boe_ero_assets.py --check
```

The builder refuses to replace a changed CoNLL-U file because it may contain manual annotation. Generate to a new path with `--conllu-output` when a fresh copy is needed.

## Alignment decisions

The earlier exploratory export counted 277 rows because it matched repeated printed numbers independently. The canonical alignment has 276 records:

- `BOR-CORBO-BOE-02-039` preserves a Portuguese item 39 with no corresponding printed Bororo item. It remains in the parallel TSV and website but is omitted from CoNLL-U because an empty sentence block would be invalid.
- In text 7, the Portuguese numbering omits 50 and prints 51 twice. The two translations are aligned positionally to Bororo 50 and 51. The mismatch is preserved in `source_number` and `translation_number` and is not silently renumbered.

Several source strings contain Unicode private-use characters inherited from a special font. They remain unchanged pending inspection of the original font or another authoritative witness.
