# CorBo AI intent evaluation

## Frozen challenge set

Evaluation set `1.0-challenge` contains 30 items frozen before the complete run: 15 positive, 5 ambiguous, and 10 boundary cases. Portuguese and English inputs test person/number, 1PL clusivity, irrealis/future, progressive aspect, negation, required arguments, ambiguity, and predicates outside the controlled lexicon.

The AI layer is evaluated only as an intent parser. It does not generate or license Bororo forms. Intent gold uses language-neutral semantic labels. Deterministic validation and Bororo subject realization read the licensed inventory in `docs/data/generator-frames.json`.

## First complete run — 2026-10-03

| Measure | Result |
|---|---:|
| Cases evaluated | 30/30 |
| Transport failures | 0 |
| Explicit intent gold | 20/20 |
| Validator decisions | 30/30 |
| Licensed subject realizations | 16/16 |
| Ambiguous cases | 5/5 |
| Boundary cases | 10/10 |

These figures describe performance on this controlled frozen challenge set. They are not an estimate of unrestricted natural-language or Bororo generation accuracy.

## Governance

The gold set, grammar, and parser instructions must not be changed retrospectively to make a run pass. A genuine annotation correction or protocol change requires a new evaluation-set version and a documented reason. Transient endpoint failures are retried and reported separately from model disagreements.

Excluded from this evaluation are the `-iure` forms and the focus/copular construction pending separate analysis.
