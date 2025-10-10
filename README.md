
# Bororo Corpus v2 (Structured Base)

**Build date:** 2025-10-10 13:06:43

This folder contains the *clean + structured* base for the Bororo Corpus new release.

## Contents

- `structured_texts.csv` — sections parsed from the ritual/narrative `.txt` files. Columns:
  - `text_id`: stable identifier (`<filename>_<section>`)
  - `source_file`: original path
  - `section_number`: numeric section (if available)
  - `title`: section header line
  - `lines_count`, `char_count`: quick diagnostics
  - `content`: full raw content (unchanged)

- `structured_texts.jsonl` — the same data, newline-delimited JSON for easy streaming.

- `unified_parallel.csv` — (if present) a schema-normalized merge of the uploaded CSVs
  (`bororo_corpus_parallel.csv`, `monolingual.csv`, `pedrosa_monolingue.csv`, `bororo_nt_clean.csv`)
  with columns:
  - `uid`: source-tagged id
  - `source`: short tag for file-of-origin
  - `src_lang`, `tgt_lang`: ISO-style codes when detected (e.g., `bor`, `por`)
  - `src_text`, `tgt_text`

## Next steps (Step 2 — Linguistic Enrichment)

- Sentence alignment (if needed) and sentence IDs
- Morphological analysis + UPOS/FEATS using your Bororo analyzer
- UD-style dependency export (`.conllu`) + interlinear glosses
- Web viewer export (HTML/Jinja2) for Boe eno moto

---

If you need different columns or an alternative JSON schema, we can regenerate quickly.
