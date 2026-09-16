# CorBo editorial guidelines

## 1. Documentary principle

The source witness is primary. Editorial cleanup must not erase documentary variation. Apparent spelling errors, historical orthographies, variant forms, repetitions, and performance structure are retained in the source layer unless there is explicit evidence that they are extraction artifacts.

## 2. Layers

CorBo distinguishes at least:

- `source`: wording as attested in the documentary witness;
- `curated`: structurally recovered text with source boundaries made explicit;
- `parallel`: aligned Bororo and Portuguese units where the source supports alignment;
- `normalized`: optional future searchable orthographic layer;
- `commentary`: ethnographic, lexical, editorial, or explanatory material that is not running corpus text.

A normalized layer must never replace `source`.

## 3. Units

`source_unit` is the neutral default. It must not be renamed `sentence` until linguistic sentence segmentation has been established.

Recommended units by genre:

- narrative/prose: source unit, later sentence;
- ritual song: verse/strophe/performance unit;
- ritual performance: performance unit;
- discourse: source unit, later sentence where appropriate;
- lexical/list material: entry/item, not sentence.

## 4. Parallel data

Portuguese is provisionally stored as `translation_or_interpretation_pt` unless the documentary source establishes that it is a translation.

Alignment status should distinguish at least:

- `candidate`
- `verified_structural`
- `verified_editorial`

`verified_structural` means that documentary structure strongly supports the pair. It does not assert literal translation equivalence.

## 5. Identifiers

Text IDs: `BOR-CORBO-<collection/work-id>`.

Units derive from the text ID, e.g. `BOR-CORBO-HM001-u001`.

IDs must remain stable after public release. Titles, filenames, orthography, and metadata may change without changing the stable ID.

## 6. Annotation boundary

UD/CoNLL-U syntactic annotation is not part of CorBo vNext. The documentary corpus may later be referenced by a separate annotated corpus/treebank using stable CorBo text and sentence IDs.

## 7. Provenance

Every text should record, where known: source file/witness, narrator/speaker/performer, collector/documenter, place, date/date range, genre, translation status, editorial status, and relevant rights/access information.
