#!/usr/bin/env python3
"""Build a reproducible, conservative lexical model from CorBo CoNLL-U.

Usage: python3 scripts/train_tokenizer.py
Only public CoNLL-U columns FORM, LEMMA, UPOS are read. No review files.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
OUTPUT = ROOT / "docs/data/tokenizer-model.json"
PREFIXES = ("ce", "pa", "ta", "tu", "i", "a", "u", "e")
SUFFIXES = ("modukare", "modure", "re", "do")
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


def train(rows):
    forms = Counter()
    analyses = defaultdict(Counter)
    families = defaultdict(Counter)
    for form, lemma, upos in rows:
        forms[form] += 1
        analyses[form][(lemma, upos)] += 1
        if lemma:
            families[lemma][form] += 1
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
        families = pattern["lemma_count"]
        tokens = pattern["tokens"]
        if families >= 10 and tokens >= 50:
            grade = "high_distributional"
        elif families >= 5 and tokens >= 20:
            grade = "medium_distributional"
        else:
            grade = "low_distributional"
        pattern["evidence_grade"] = grade
        pattern["linguistically_confirmed"] = False
    # Attach independent cross-lemma support to each proposed segmentation.
    # A pattern's distributional grade is not linguistic validation.
    pattern_index = {
        (p["position"], p["material"]): p
        for p in cross_lemma_patterns
    }
    for form, candidate in candidates.items():
        parts = candidate["segments"]
        matched = []
        for prefix in PREFIXES:
            if len(parts) >= 2 and parts[0] == prefix:
                p = pattern_index.get(("prefix", prefix))
                if p:
                    matched.append(p)
                break
        for ending in SUFFIXES:
            suffix_parts = ["modu", "ka", "re"] if ending == "modukare" else ["modu", "re"] if ending == "modure" else [ending]
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
                        pieces += ["modu", "ka", "re"] if suffix == "modukare" else ["modu", "re"] if suffix == "modure" else [suffix]
                    options.append((support, pieces))
        options = [(support, parts) for support, parts in options if support >= MIN_SUPPORT]
        if options:
            options.sort(key=lambda x: (-x[0], -len(x[1]), x[1]))
            candidates[form] = {"segments": options[0][1], "support": options[0][0], "status": "proposed"}
    # Discover recurring grammatical endings in lemma-linked forms.
    # Counts are evidence for candidate discovery, never confirmation.
    suffix_evidence = defaultdict(lambda: {"types": 0, "tokens": 0, "examples": []})
    for form, item in candidates.items():
        parts = item["segments"]
        for ending in ("re", "do", "modure", "modukare"):
            suffix_parts = {"re": ["re"], "do": ["do"], "modure": ["modu", "re"], "modukare": ["modu", "ka", "re"]}[ending]
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
