#!/usr/bin/env python3
"""Export only public lexical fields from a private Bororo dictionary CSV.

The source spreadsheet must remain outside this repository. Export a CSV from
Drive locally, then run:
 python3 scripts/export_dictionary_public.py /private/path/dicionario.csv
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("id", "entry", "ipa", "pos", "definition", "example_sent", "scientific_name", "wiki_link", "pic_link", "comment")
def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: export_dictionary_public.py /path/outside/repo/dicionario.csv")
    source = Path(sys.argv[1]).resolve()
    if source.is_relative_to(ROOT):
        raise SystemExit("Keep the private source outside the repository.")
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"entry", "definition", "pos"}.issubset(reader.fieldnames or []):
            raise SystemExit("Unexpected dictionary columns.")
        rows = []
        for row in reader:
            if not (row.get("entry") or "").strip():
                continue
            item = {k: (row.get(k) or "").strip() for k in FIELDS}
            item["lemma_key"] = re.sub(r"\s*\d+$", "", item["entry"]).strip().casefold()
            rows.append(item)
    output = ROOT / "docs/data/dicionario-bororo-publico.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"source": "Dicionário Bororo (Google Drive; original não publicado)", "entries": rows}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"{len(rows)} entradas públicas exportadas para {output.relative_to(ROOT)}")
if __name__ == "__main__":
    main()
