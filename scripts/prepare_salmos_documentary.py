#!/usr/bin/env python3
"""Prepare a lossless, reviewable documentary export of the Bororo Psalter.

Does not alter the source or claim that verse=0 denotes a real verse.
The canticles appended to Psalm 150 are kept in a separate collection.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CorBo/Scripture_Sources/salmos.json"
MARKER = "CÂNTICOS DO BREVIÁRIO"


def prepare(source):
    raw = json.loads(source.read_text(encoding="utf-8"))
    entries = raw["entries"]
    psalms, canticles = [], []
    for pos, entry in enumerate(entries, 1):
        chapter = entry["capitulo"]
        verse = entry["versiculo"]
        original = entry["texto"]
        if not isinstance(chapter, int) or not 1 <= chapter <= 150:
            raise ValueError(f"Capítulo inválido no registro {pos}")
        if not isinstance(original, str) or not original.strip():
            raise ValueError(f"Texto vazio no registro {pos}")
        text = original
        if MARKER in text:
            if chapter != 150:
                raise ValueError(f"Marcador de cânticos inesperado no registro {pos}")
            if len(canticles):
                raise ValueError("Marcador de cânticos duplicado")
            before, after = text.split(MARKER, 1)
            text = before
            canticles.append({
                "id": "canticos_breviario_001",
                "source_entry": pos,
                "source_chapter": chapter,
                "heading": MARKER,
                "text": after,
                "segmentation_status": "unsegmented_source_appendix",
            })
            if MARKER + after != original[len(before):]:
                raise AssertionError("Falha na preservação dos cânticos")
        psalms.append({
            "id": f"salmos_{chapter:03d}_{pos:03d}",
            "source_entry": pos,
            "book": "Salmos",
            "chapter": chapter,
            "verse": verse if verse > 0 else None,
            "reference": f"Sl {chapter},{verse}" if verse > 0 else f"Sl {chapter}",
            "text": text,
            "segmentation_status": "source_verse" if verse > 0 else "chapter_block_unsegmented",
        })
    counts = Counter(p["chapter"] for p in psalms)
    missing = [n for n in range(1, 151) if n not in counts]
    if missing:
        raise ValueError(f"Salmos ausentes: {missing}")
    if len(canticles) != 1:
        raise ValueError("Esperado um único apêndice de cânticos no Salmo 150")
    # Exact reconstruction, including original newlines and whitespace.
    for pos, (entry, psalm) in enumerate(zip(entries, psalms), 1):
        reconstructed = psalm["text"]
        if pos == canticles[0]["source_entry"]:
            reconstructed += MARKER + canticles[0]["text"]
        if reconstructed != entry["texto"]:
            raise AssertionError(f"Registro {pos} não preservado")
    return {
        "schema_version": "0.1",
        "book": "Salmos",
        "status": "documentary_provisional",
        "source": str(SOURCE.relative_to(ROOT)),
        "units": psalms,
    }, {
        "schema_version": "0.1",
        "collection": "Cânticos do Breviário",
        "status": "unsegmented_pending_review",
        "source": str(SOURCE.relative_to(ROOT)),
        "units": canticles,
    }, {
        "source_entries": len(entries),
        "psalms_represented": len(counts),
        "verse_level_entries": sum(p["verse"] is not None for p in psalms),
        "chapter_blocks": sum(p["verse"] is None for p in psalms),
        "canticle_appendices": len(canticles),
        "missing_psalms": missing,
        "warning": "Não inferir versículos dos blocos; cânticos exigem revisão de referências.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/salmos_documentais")
    args = parser.parse_args()
    psalms, canticles, report = prepare(SOURCE)
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, obj in (
        ("salmos_unidades_documentais.json", psalms),
        ("canticos_breviario_unidades_documentais.json", canticles),
        ("relatorio.json", report),
    ):
        (args.output / filename).write_text(
            json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
