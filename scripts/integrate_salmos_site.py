#!/usr/bin/env python3
"""Integrate published Psalms into catalog and documentary statistics.

Run after publish_salmos_documentary.py. Does not touch unrelated local edits.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [ROOT / "docs/salmos.html", ROOT / "docs/data/salmos.json"]
for path in required:
    if not path.is_file():
        raise SystemExit(f"Arquivo ausente: {path}. Execute publish_salmos_documentary.py primeiro.")

catalog = ROOT / "docs/catalogo.html"
text = catalog.read_text(encoding="utf-8")
if 'href="salmos.html"' not in text:
    anchor = '<div class="item"><div><h3><a href="sabedoria.html">'
    card = ('<div class="item"><div><h3><a href="salmos.html">Salmos</a></h3>'
            '<span class="badge">segmentação provisória</span></div>'
            '<p class="muted">150 salmos em bororo, com 185 registros documentais; '
            '145 blocos ainda sem divisão por versículos. Cânticos anexos separados para revisão.</p>'
            '<div class="meta">Bororo<br>185 unidades documentais</div></div>')
    if anchor not in text:
        raise SystemExit("Âncora de Sabedoria não encontrada no catálogo")
    catalog.write_text(text.replace(anchor, card + anchor, 1), encoding="utf-8")

for name in ("index.html", "statistics.html"):
    path = ROOT / "docs" / name
    text = path.read_text(encoding="utf-8")
    if "'salmos'" not in text and '"salmos"' not in text:
        anchor = "'sabedoria'," if name == "index.html" else '"sabedoria",'
        if anchor not in text:
            raise SystemExit(f"Âncora não encontrada: {name}")
        text = text.replace(anchor, anchor + ("'salmos'," if name == "index.html" else '"salmos",'), 1)
    if name == "statistics.html":
        text = text.replace(
            "Gênesis e Salmos constam entre as fontes do projeto, mas não integram esta contagem de leitores documentais.",
            "Gênesis consta entre as fontes do projeto, mas não integra esta contagem. Salmos inclui 185 registros documentais, dos quais 145 permanecem sem segmentação por versículo."
        )
    path.write_text(text, encoding="utf-8")
print("Catálogo, página inicial e estatísticas integrados aos Salmos.")
