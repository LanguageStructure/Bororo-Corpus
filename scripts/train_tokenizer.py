#!/usr/bin/env python3
"""Build a reproducible, conservative lexical model from CorBo CoNLL-U.

Usage: python3 scripts/train_tokenizer.py
Reads FORM, LEMMA, UPOS and a separate linguist-reviewed analysis file.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import json
from bororo_initial_alternations import find_attested_analysis
from bororo_combined_morphology import analyze_combined

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUTPUT = ROOT / "docs/data/tokenizer-model.json"
REVIEWED_AIMO = ROOT / "CorBo_vNext/annotations/aimo_reviewed_20261018.json"
PREFIXES = ("ce", "pa", "ta", "tu", "i", "a", "u", "e")
SUFFIXES = ("modukare", "modure", "kare", "re", "do")
MIN_SUPPORT = 3
# Linguistic safeguards: frequent strings are not automatically morphemes.
REJECTED_SUFFIXES = {"je"}  # -je is not a suffix in Bororo.
CAUTION_ENDINGS = {"dure"}  # May cross morpheme boundaries; never infer -dure.




def read_conllu(path):
    for line in path.open(encoding="utf-8-sig"):
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 4 or not cols[0].isdigit():
            continue
        form, lemma, upos = cols[1:4]
        if not form or form == "_":
            continue
        yield form.casefold(), lemma.casefold() if lemma != "_" else "", upos


def load_reviewed_aimo(path=REVIEWED_AIMO):
    """Load explicitly reviewed forms; no general rule is inferred."""
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "linguist_confirmed_examples_not_general_rules":
        raise ValueError("Unexpected review status")
    reviewed = {}
    entries = list(data["analyses"])
    for paradigm in data.get("paradigms", []):
        entries.extend(paradigm["analyses"])
    for item in entries:
        form = item["surface"].casefold()
        segments = [part.casefold() for part in item["segments"]]
        if not segments or "".join(segments) != form:
            raise ValueError("Invalid reviewed segmentation: " + form)
        if form in reviewed:
            raise ValueError("Duplicate reviewed form: " + form)
        reviewed[form] = segments
    return reviewed


def train(rows, reviewed_aimo=None):
    forms = Counter()
    analyses = defaultdict(Counter)
    families = defaultdict(Counter)
    for form, lemma, upos in rows:
        forms[form] += 1
        analyses[form][(lemma, upos)] += 1
        if lemma:
            families[lemma][form] += 1
    # UPOS is a contextual annotation, not an inherent noun/verb class of
    # a Bororo lexical root. Morphological families must remain UPOS-neutral.
    # Paradigms are grouped by annotated lemma; keep only informative
    # families with multiple distinct surface forms and sufficient tokens.
    paradigms = {}
    for lemma, family in sorted(families.items()):
        if not lemma or len(family) < 2:
            continue
        total = sum(family.values())
        if total < MIN_SUPPORT:
            continue
        paradigms[lemma] = {
            "types": len(family),
            "tokens": total,
            "forms": [
                {"form": form, "frequency": count}
                for form, count in sorted(family.items(), key=lambda item: (-item[1], item[0]))
            ],
        }
    # Describe surface correspondences within each attested lemma family.
    # These are descriptive alignments, NOT licensed morpheme boundaries.
    paradigm_alternations = {}
    for lemma, record in paradigms.items():
        if lemma not in forms or len(lemma) < 3:
            continue
        alignments = []
        for item in record["forms"]:
            form = item["form"]
            if form == lemma:
                continue
            if form.endswith(lemma):
                alignments.append({"form": form, "relation": "prefix", "material": form[:-len(lemma)], "frequency": item["frequency"]})
            elif form.startswith(lemma):
                alignments.append({"form": form, "relation": "suffix", "material": form[len(lemma):], "frequency": item["frequency"]})
            else:
                alignments.append({"form": form, "relation": "nonconcatenative_or_unresolved", "frequency": item["frequency"]})
        if alignments:
            paradigm_alternations[lemma] = alignments
    # Aggregate cross-lemma evidence for recurrent surface additions.
    # Count distinct lemmas, not merely tokens, to avoid a single frequent
    # paradigm being mistaken for a productive grammatical pattern.
    cross_lemma = defaultdict(lambda: {"lemmas": set(), "types": 0, "tokens": 0, "examples": []})
    for lemma, alignments in paradigm_alternations.items():
        for item in alignments:
            relation = item["relation"]
            material = item.get("material", "")
            if relation not in ("prefix", "suffix") or not material:
                continue
            if relation == "suffix" and (material in REJECTED_SUFFIXES or material in CAUTION_ENDINGS):
                continue
            key = (relation, material)
            record = cross_lemma[key]
            record["lemmas"].add(lemma)
            record["types"] += 1
            record["tokens"] += item["frequency"]
            if len(record["examples"]) < 6:
                record["examples"].append({"lemma": lemma, "form": item["form"]})
    cross_lemma_patterns = [
        {"position": position, "material": material,
         "lemma_count": len(record["lemmas"]), "types": record["types"],
         "tokens": record["tokens"], "examples": record["examples"]}
        for (position, material), record in cross_lemma.items()
        if len(record["lemmas"]) >= 3
    ]
    cross_lemma_patterns.sort(key=lambda x: (-x["lemma_count"], -x["tokens"], x["position"], x["material"]))
    # Rank cross-lemma patterns by independent lexical support.
    # Confidence is distributional only, never a claim of grammatical truth.
    for pattern in cross_lemma_patterns:
        lemma_family_count = pattern["lemma_count"]
        tokens = pattern["tokens"]
        if lemma_family_count >= 10 and tokens >= 50:
            grade = "high_distributional"
        elif lemma_family_count >= 5 and tokens >= 20:
            grade = "medium_distributional"
        else:
            grade = "low_distributional"
        pattern["evidence_grade"] = grade
        pattern["linguistically_confirmed"] = False
    # Observed grammatical units and their contiguous token sequences.
    # These are distributional statistics, not claims of internal morphology.
    grammatical = {"u", "nu", "re"}
    grammatical_counts = {unit: forms[unit] for unit in sorted(grammatical)}
    # Observed surface forms alone do not license a morphological boundary.
    # Candidate analyses must share a CoNLL-U lemma with an independently
    # attested base. Enumerate prefix+base+suffix as well as single affixes.
    # Surface segmentation candidates require evidence of a base attested
    # independently AND an identical lemma family; no b/w or k/g guessing.
    candidates = {}
    for form, n in forms.items():
        options = []
        related_lemmas = {lemma for lemma, _upos in analyses[form] if lemma}
        for lemma in related_lemmas:
            if form == lemma or lemma not in forms or (len(lemma) < 3 and lemma not in {"u", "ce", "pa", "ta", "i", "a", "e", "tu"}):
                continue
            support = families[lemma][form]
            for prefix in ("", *PREFIXES):
                for suffix in ("", *SUFFIXES):
                    if not prefix and not suffix:
                        continue
                    if form != prefix + lemma + suffix:
                        continue
                    # Short grammatical lemmas require an overt ending;
                    # avoid arbitrary splits of common short strings.
                    if len(lemma) < 3 and (prefix or not suffix):
                        continue
                    pieces = ([prefix] if prefix else []) + [lemma]
                    if suffix:
                        pieces += ["modu", "ka", "re"] if suffix == "modukare" else ["modu", "re"] if suffix == "modure" else ["ka", "re"] if suffix == "kare" else [suffix]
                    options.append((support, pieces))
        options = [(support, parts) for support, parts in options if support >= MIN_SUPPORT]
        if options:
            options.sort(key=lambda x: (-x[0], -len(x[1]), x[1]))
            candidates[form] = {"segments": options[0][1], "support": options[0][0], "status": "proposed"}
    # Apply productive initial-consonant correspondences only to observed
    # surface forms with an explicitly annotated lemma. These remain
    # rule-supported proposals, not manually reviewed analyses.
    # Lexical exceptions can be added to the exception set after review.
    initial_alternation_exceptions = set()
    for surface in forms:
        if surface in candidates:
            continue
        for lemma, _upos in analyses[surface]:
            proposed = find_attested_analysis(surface, lemma, initial_alternation_exceptions)
            if proposed:
                candidates[surface] = {
                    **proposed, "support": families[lemma][surface],
                }
                break
    # Combined analyses are proposed only for attested surface/lemma pairs.
    # Do not overwrite explicit confirmations applied below. Unlike simple
    # surface splits, these retain the lexical lemma and stem allomorph.
    for surface in forms:
        for lemma, _upos in analyses[surface]:
            proposal = analyze_combined(surface, lemma)
            if proposal:
                candidates[surface] = {
                    **proposal, "support": families[lemma][surface],
                }
                break
    # A confirmed b>w analysis outranks a merely distributional suffix split.
    # The source CoNLL-U lemma must explicitly support the correspondence.
    # Other initial-alternation candidates remain provisional.
    awure = find_attested_analysis("awure", "bure")
    if "awure" in forms and any(lemma == "bure" for lemma, _ in analyses["awure"]):
        candidates["awure"] = {
            **awure, "support": families["bure"]["awure"],
            "status": "linguistically_confirmed",
            "evidence": "linguist_confirmed_b_to_w",
        }
    # Linguistically confirmed segmentations, applied only to attested forms.
    # These are deliberately separate from distributional proposals. They do
    # not authorize splitting other words with similar character sequences.
    confirmed = {
        "ure": ["u", "re"], "ire": ["i", "re"],
        "are": ["a", "re"], "cere": ["ce", "re"],
        "pare": ["pa", "re"], "tare": ["ta", "re"],
        "ere": ["e", "re"], "imode": ["i", "modu", "re"],
        "nure": ["nu", "re"],
        "iere": ["i", "ie", "re"],
        "iorudumodukare": ["i", "jorudu", "modu", "ka", "re"],
        "iorudukare": ["i", "jorudu", "ka", "re"],
        "itonaregedu": ["it", "onarege", "du"],
    }
    # Reviewed mako paradigm: the orthographic g is retained in the
    # stem allomorph mago; do not infer a general k~g rewrite rule.
    confirmed_mako = {
        "imago": ["i", "mago"], "amago": ["a", "mago"],
        "pamago": ["pa", "mago"], "cemago": ["ce", "mago"],
        "tamago": ["ta", "mago"], "emago": ["e", "mago"],
        "tumago": ["tu", "mago"],
    }
    confirmed.update(confirmed_mako)
    # Reviewed aimo forms supersede previous ce+daimo/pa+daimo guesses.
    # Preserve attestation gating; never invent unattested inflections.
    reviewed = load_reviewed_aimo() if reviewed_aimo is None else reviewed_aimo
    confirmed.update(reviewed)
    for surface, segments in confirmed.items():
        if surface in forms:
            candidates[surface] = {
                "segments": segments, "support": forms[surface],
                "status": "linguistically_confirmed",
                "evidence": "linguist_reviewed_analysis" if surface in reviewed else "explicit_confirmed_analysis",
            }
    # A nasal onset in i(n)- and the t onset before vowel-initial bases
    # require lexical confirmation; never infer them from spelling alone.
    # Keep explicitly reviewed forms separate from productive proposals.
    confirmed_onset_alternations = {
        "itonaregedu": ["it", "onarege", "du"],
    }
    for surface, segments in confirmed_onset_alternations.items():
        if surface in forms:
            candidates[surface] = {
                "segments": segments, "support": forms[surface],
                "status": "linguistically_confirmed",
                "evidence": "reviewed_onset_alternation",
            }
    # Do not create or license unattested forms from an apparent paradigm.
    for nonexistent in ("tabiapagado", "ibiapagare", "iakore", "eakore"):
        candidates.pop(nonexistent, None)
    # Attach independent cross-lemma support to each proposed segmentation.
    # A pattern's distributional grade is not linguistic validation.
    pattern_index = {
        (p["position"], p["material"]): p
        for p in cross_lemma_patterns
    }
    for form, candidate in candidates.items():
        parts = candidate["segments"]
        matched = []
        # A two-part form ending in a licensed suffix is base+suffix,
        # not automatically prefix+base (e.g. a+do).
        for prefix in PREFIXES:
            if len(parts) >= 2 and parts[0] == prefix and not (len(parts) == 2 and parts[-1] in SUFFIXES):
                p = pattern_index.get(("prefix", prefix))
                if p:
                    matched.append(p)
                break
        for ending in SUFFIXES:
            suffix_parts = ["modu", "ka", "re"] if ending == "modukare" else ["modu", "re"] if ending == "modure" else ["ka", "re"] if ending == "kare" else [ending]
            if parts[-len(suffix_parts):] == suffix_parts:
                p = pattern_index.get(("suffix", ending))
                if p:
                    matched.append(p)
                break
        candidate["cross_lemma_evidence"] = [
            {"position": p["position"], "material": p["material"],
             "lemma_count": p["lemma_count"], "evidence_grade": p["evidence_grade"]}
            for p in matched
        ]
        # Every proposed boundary needs independent evidence; a strong
        # prefix cannot compensate for an unsupported suffix.
        boundaries = len(parts) - 1
        candidate["evidence_grade"] = (
            min((p["evidence_grade"] for p in matched),
                key=lambda g: {"low_distributional": 1, "medium_distributional": 2, "high_distributional": 3}[g])
            if len(matched) >= boundaries else "unrated"
        )
    # Discover recurring grammatical endings in lemma-linked forms.
    # Counts are evidence for candidate discovery, never confirmation.
    suffix_evidence = defaultdict(lambda: {"types": 0, "tokens": 0, "examples": []})
    for form, item in candidates.items():
        parts = item["segments"]
        for ending in ("re", "do", "kare", "modure", "modukare"):
            suffix_parts = {"re": ["re"], "do": ["do"], "kare": ["ka", "re"], "modure": ["modu", "re"], "modukare": ["modu", "ka", "re"]}[ending]
            if parts[-len(suffix_parts):] == suffix_parts:
                record = suffix_evidence[ending]
                record["types"] += 1
                record["tokens"] += forms[form]
                if len(record["examples"]) < 8:
                    record["examples"].append(form)
    suffix_evidence = dict(sorted(suffix_evidence.items()))
    # Distributional discovery from recurring word endings, independent of
    # lemma annotations. This is evidence for investigation, not segmentation.
    ending_counts = defaultdict(lambda: {"types": 0, "tokens": 0, "examples": []})
    for form, freq in forms.items():
        if len(form) < 5 or not form.isalpha():
            continue
        for width in range(2, min(6, len(form) - 2) + 1):
            ending = form[-width:]
            record = ending_counts[ending]
            record["types"] += 1
            record["tokens"] += freq
            if len(record["examples"]) < 5:
                record["examples"].append(form)
    recurrent_endings = {
        ending: record for ending, record in sorted(ending_counts.items())
        if record["types"] >= 5 and record["tokens"] >= 20 and ending not in REJECTED_SUFFIXES
    }
    # Compare raw distributional evidence with lemma-supported boundaries.
    # Never automatically split from character frequencies alone.
    corroborated_endings = {}
    for ending, record in recurrent_endings.items():
        matching = suffix_evidence.get(ending)
        if matching and ending not in CAUTION_ENDINGS and ending not in REJECTED_SUFFIXES:
            corroborated_endings[ending] = {
                **record,
                "lemma_supported_types": matching["types"],
                "lemma_supported_tokens": matching["tokens"],
                "evidence": "distributional+lemma",
            }
    return {
        "schema": "corbo-tokenizer-model/v1",
        "linguistic_assumptions": {
            "lexical_roots_inherently_noun_verb_distinct": False,
            "upos_role": "contextual_syntactic_annotation_not_lexical_root_class",
            "allomorph_classes": "initial_consonant_rules_plus_lexeme_specific_reviewed_examples",
            "initial_consonant_rules": {"b": "w", "p": "b", "t": "d", "k": "g", "c": "j"},
            "initial_consonant_rule_scope": "prefixation_only; b>w general, others defaults with exceptions",
        },
        "source": str(SOURCE.relative_to(ROOT)),
        "min_support": MIN_SUPPORT,
        "grammatical_unit_counts": grammatical_counts,
        "grammatical_unit_attested": {unit: bool(forms[unit]) for unit in sorted(grammatical)},
        "types": len(forms),
        "tokens": sum(forms.values()),
        "paradigm_count": len(paradigms),
        "paradigms": paradigms,
        "paradigm_alternations": paradigm_alternations,
        "cross_lemma_patterns": cross_lemma_patterns,
        "lexicon": {
            form: {
                "frequency": freq,
                "analyses": [
                    {"lemma": lemma, "upos": upos, "frequency": n}
                    for (lemma, upos), n in analyses[form].most_common()
                ],
            }
            for form, freq in sorted(forms.items())
        },
        "candidates": dict(sorted(candidates.items())),
        "suffix_evidence": suffix_evidence,
        "recurrent_endings": recurrent_endings,
        "corroborated_endings": corroborated_endings,
        "rejected_suffixes": sorted(REJECTED_SUFFIXES),
        "caution_endings": sorted(CAUTION_ENDINGS),
        "excluded_from_suffix_inference": sorted(REJECTED_SUFFIXES | CAUTION_ENDINGS),
    }


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing CoNLL-U: {SOURCE}")
    model = train(read_conllu(SOURCE))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(model, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{model['types']} types; {model['tokens']} tokens; {len(model['candidates'])} candidate segmentations -> {OUTPUT}")


if __name__ == "__main__":
    main()
