"""Conservative, attestation-gated initial-consonant alternations in Bororo.

These are orthographic correspondences after prefixation. b>w is general;
p>b, t>d, k>g, c>j are defaults with lexical exceptions. Do not
apply these changes internally or to unprefixed stems.
"""
GENERAL = {"b": "w"}
DEFAULT = {"p": "b", "t": "d", "k": "g", "c": "j"}
PERSON_PREFIXES = ("ce", "pa", "ta", "tu", "i", "a", "e", "u")


def prefixed_stem(lemma, exceptions=()):
    """Return possible stem after prefixation, or None for exceptions."""
    if not lemma or lemma in exceptions:
        return None
    first = lemma[0]
    change = GENERAL.get(first, DEFAULT.get(first))
    return change + lemma[1:] if change else lemma


def find_attested_analysis(surface, lemma, exceptions=()):
    """Find prefix+allomorph only when surface and lemma are supplied.

    Never generate an unattested surface form. The return value preserves
    the surface stem and the underlying lexical lemma separately.
    """
    if not lemma or not surface or lemma in exceptions:
        return None
    stem = prefixed_stem(lemma, exceptions)
    if not stem or stem == lemma or surface == lemma:
        return None
    for prefix in PERSON_PREFIXES:
        if surface == prefix + stem:
            return {"segments": [prefix, stem], "lemma": lemma,
                    "stem_allomorph": stem, "alternation": lemma[0] + ">" + stem[0],
                    "status": "rule_supported_attested",
                    "evidence": "co_nllu_lemma_and_surface"}
    return None
