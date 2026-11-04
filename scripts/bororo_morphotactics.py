"""Conservative, linguist-confirmed Bororo verbal morphotactics.

This module does not generate unattested word forms. A missing combination
is UNKNOWN, not ungrammatical. Surface forms are distinct from underlying
morpheme sequences.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

FINAL_MARKERS = {
    "re": "IND",
    "wo": "SBJV",
    "ie": "INDIR",
    "iagu": "QUOT",
}
ASPECT_ORDER = ("godu", "modu", "nu")
CONFIRMED_SEQUENCES = {
    ("godu", "re"): "frequent",
    ("godu", "nu", "re"): "rare",
    ("modu", "re"): "confirmed",
    ("godu", "modu", "re"): "confirmed",
}
UNATTESTED_SEQUENCES = {
    ("godu", "modu", "nu", "re"),
}
EXCLUDED_PAIRS = {
    ("nu", "wo"),
    ("nu", "ie"),
    ("nu", "iagu"),
}


@dataclass(frozen=True)
class Assessment:
    status: str
    reason: str
    underlying: tuple[str, ...]
    surface: str


def realize(morphemes: Sequence[str]) -> str:
    """Apply the confirmed local alternation modu+re > mode."""
    parts = list(morphemes)
    result = []
    i = 0
    while i < len(parts):
        if parts[i:i + 2] == ["modu", "re"]:
            result.append("mode")
            i += 2
        else:
            result.append(parts[i])
            i += 1
    return "".join(result)


def assess(suffixes: Sequence[str]) -> Assessment:
    """Assess suffix sequence, without claiming an unattested form exists.

    Accepts suffixes only, excluding the lexical base. 'unknown' indicates
    insufficient evidence; 'excluded' is reserved for explicit restrictions.
    """
    parts = tuple(suffixes)
    surface = realize(parts)
    if not parts or parts[-1] not in FINAL_MARKERS:
        return Assessment("unknown", "Final marker not established", parts, surface)
    if sum(part in FINAL_MARKERS for part in parts) != 1:
        return Assessment("excluded", "Multiple markers in the same final slot", parts, surface)
    if any(part not in ASPECT_ORDER for part in parts[:-1]):
        return Assessment("unknown", "Unrecognized or unreviewed suffix", parts, surface)
    indices = [ASPECT_ORDER.index(part) for part in parts[:-1]]
    if indices != sorted(set(indices)):
        return Assessment("excluded", "Confirmed aspect ordering or repetition violated", parts, surface)
    if "nu" in parts and parts[-1] != "re":
        return Assessment("excluded", "Progressive nu requires final re", parts, surface)
    if parts in UNATTESTED_SEQUENCES:
        return Assessment("unattested", "Predicted ordering, no confirmed occurrence", parts, surface)
    if parts in CONFIRMED_SEQUENCES:
        return Assessment("confirmed", CONFIRMED_SEQUENCES[parts], parts, surface)
    return Assessment("unknown", "Combination not yet reviewed", parts, surface)


if __name__ == "__main__":
    assert realize(("are", "godu", "modu", "re")) == "aregodumode"
    assert realize(("godu", "modu", "nu", "re")) == "godumodunure"
    assert assess(("godu", "modu", "re")).status == "confirmed"
    assert assess(("godu", "nu", "re")).status == "confirmed"
    assert assess(("godu", "modu", "nu", "re")).status == "unattested"
    assert assess(("nu", "wo")).status == "excluded"
    assert assess(("modu", "wo")).status == "unknown"
    print("Bororo morphotactics checks passed")
