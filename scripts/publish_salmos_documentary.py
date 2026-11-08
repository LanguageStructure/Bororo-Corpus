#!/usr/bin/env python3
"""Publish validated Psalms as a documentary reader (not UD annotations)."""
import json
from pathlib import Path
from prepare_salmos_documentary import prepare, SOURCE, ROOT

def main():
    psalms, canticles, report = prepare(SOURCE)
    units = []
    for row in psalms["units"]:
        units.append({
            "id": row["id"],
            "document_id": f"salmos_{row['chapter']:03d}",
            "collection": "Antigo Testamento",
            "book": "Salmos",
            "reference": row["reference"],
            "reference_provisional": row["verse"] is None,
            "source_paragraphs": str(row["source_entry"]),
            "text": row["text"],
            "source_text_original": row["text"],
            "segmentation_status": row["segmentation_status"],
        })
    data = {
        "collection": "Antigo Testamento",
        "book": "Salmos",
        "source": psalms["source"],
        "status": "documentary_provisional",
        "segmentation_method": "40 verse-level entries; 145 unsegmented chapter blocks",
        "units": units,
    }
    output = ROOT / "docs/data/salmos.json"
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    template = (ROOT / "docs/sabedoria.html").read_text(encoding="utf-8")
    template = template.replace("Sabedoria", "Salmos").replace("sabedoria.json", "salmos.json")
    old = "319 unidades de leitura propostas, provenientes de 200 registros documentais. Segmentação e algumas referências em revisão. O texto original está disponível em cada unidade."
    new = ("185 unidades documentais em 150 salmos. Os Salmos 1–5 têm 40 registros por versículo; "
           "os outros 145 registros são blocos não segmentados. Os cânticos anexados ao Salmo 150 "
           "foram separados para revisão. O texto original está disponível em cada unidade.")
    if old not in template:
        raise ValueError("A descrição do modelo Sabedoria mudou; revisar antes de publicar")
    template = template.replace(old, new)
    # Sabedoria contains a legacy second lexical panel; retain only the primary panel.
    template = template.split("<!-- corbo-1reis-lexical-v3 -->", 1)[0] + "</body></html>\\n"
    template = template.replace('<script src="./ud-pt.js">const esc=', '<script src="./ud-pt.js"></script><script>const esc=')
    (ROOT / "docs/salmos.html").write_text(template, encoding="utf-8")
    # Canonical editable copy for the local documentary editor.
    canonical = ROOT / "CorBo_vNext/texts/biblicos/salmos"
    canonical.mkdir(parents=True, exist_ok=True)
    (canonical / "salmos_unidades_documentais.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # Keep the detached canticles as a separately reviewable source, not as psalm 150.
    review = ROOT / "CorBo_vNext/texts/biblicos/salmos"
    review.mkdir(parents=True, exist_ok=True)
    (review / "canticos_breviario_unidades_documentais.json").write_text(
        json.dumps(canticles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Publicado localmente: {len(units)} unidades, {report['psalms_represented']} salmos")
    print("Arquivos: docs/data/salmos.json, docs/salmos.html e apêndice de cânticos separado")

if __name__ == "__main__":
    main()
