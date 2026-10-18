"""Attested prefix + initial allomorph + ending hypotheses.

Only analyze a form with an annotated lemma; no unattested forms are
generated. These are proposals, not linguist-confirmed segmentations.
"""
from bororo_initial_alternations import PERSON_PREFIXES, prefixed_stem

# Morphological pieces are explicit; longest ending wins.
ENDINGS = (
    ("modukare", ("modu", "ka", "re")),
    ("modure", ("modu", "re")),
    ("kare", ("ka", "re")),
    ("iagu", ("iagu",)),
    ("wo", ("wo",)),
    ("ie", ("ie",)),
    ("re", ("re",)),
)


def analyze_combined(surface, lemma, exceptions=()):
    if not surface or not lemma or lemma in exceptions:
        return None
    stem = prefixed_stem(lemma, exceptions)
    if not stem or stem == lemma:
        return None
    for prefix in PERSON_PREFIXES:
        if not surface.startswith(prefix + stem):
            continue
        remainder = surface[len(prefix + stem):]
        for ending, pieces in ENDINGS:
            if remainder == ending:
                return {
                    "segments": [prefix, stem, *pieces],
                    "lemma": lemma,
                    "stem_allomorph": stem,
                    "alternation": lemma[0] + ">" + stem[0],
                    "status": "combined_rule_proposal",
                    "evidence": "attested_surface_annotated_lemma_and_known_ending",
                }
    return None
