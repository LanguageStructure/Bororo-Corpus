"""Tokenizador e segmentador do Bororo baseado no inventário v5 do CorBo."""
from __future__ import annotations

import json
import os
import re
import unicodedata
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["Tokenizer", "Token"]
SITE = "https://languagestructure.github.io/Bororo-Corpus/data/tokenizer-v5-site.json"
_TOKEN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*|\d+|[^\w\s]", re.UNICODE)


@dataclass
class Token:
    form: str
    start: int
    end: int
    kind: str = "word"                 # word | punct | number
    segments: list = field(default_factory=list)
    underlying: list = field(default_factory=list)
    status: str = "unanalysed"         # confirmed | proposed | proposed_low_support | unanalysed
    lang_suspect: str | None = None


def _find_inventory(path=None):
    for p in (path, os.environ.get("CORBO_INVENTORY")):
        if p:
            return Path(p)
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "docs/data/tokenizer-v5-site.json"
        if cand.exists():
            return cand
    return None


class Tokenizer:
    def __init__(self, inventory: str | os.PathLike | None = None):
        p = _find_inventory(inventory)
        if p:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
        else:
            with urllib.request.urlopen(SITE, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
        self.forms = data["forms"]
        self.schema = data.get("schema")

    def tokenize(self, text: str) -> list[Token]:
        """Separa palavras, números e pontuação, preservando as posições no texto."""
        text = unicodedata.normalize("NFC", text)
        out = []
        for m in _TOKEN.finditer(text):
            f = m.group(0)
            kind = "word" if f[0].isalpha() else "number" if f.isdigit() else "punct"
            out.append(Token(f, m.start(), m.end(), kind))
        return out

    def analyze(self, text: str) -> list[Token]:
        """Como tokenize(), acrescentando segmentação e estado de revisão a cada palavra."""
        tokens = self.tokenize(text)
        for t in tokens:
            if t.kind != "word":
                continue
            e = self.forms.get(t.form.casefold())
            if not e:
                continue
            t.status = e.get("review_status", e.get("status", "unanalysed"))
            t.lang_suspect = e.get("lang_suspect")
            a = next((x for x in e.get("analyses", []) if len(x.get("segments") or []) > 1), None)
            if a:
                t.underlying = list(a.get("underlying_morphemes") or a["segments"])
                surf = a.get("surface_segments") or (a["segments"] if "".join(a["segments"]).casefold() == t.form.casefold() else None)
                if surf:  # recupera a capitalização original da forma
                    at, segs = 0, []
                    for s in surf:
                        segs.append(t.form[at:at + len(s)]); at += len(s)
                    t.segments = segs
        return tokens

    def to_conllu(self, text: str) -> str:
        lines = ["# text = " + " ".join(text.split())]
        for i, t in enumerate(self.analyze(text), 1):
            misc = []
            if t.segments:
                misc += ["Seg=" + "+".join(t.segments), "SegStatus=" + t.status]
            elif t.underlying:
                misc += ["Underlying=" + "+".join(t.underlying), "SegStatus=" + t.status]
            upos = "PUNCT" if t.kind == "punct" else "NUM" if t.kind == "number" else "_"
            lines.append("\t".join([str(i), t.form, "_", upos, "_", "_", "_", "_", "_", "|".join(misc) or "_"]))
        return "\n".join(lines) + "\n\n"
