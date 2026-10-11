#!/usr/bin/env python3
"""Export only explicitly approved thematic entries; never reads private source files."""
import argparse
import csv
import json
from pathlib import Path

THEMES = {"Fauna", "Flora e etnobotânica", "Corpo humano", "Cores",
          "Parentesco", "Verbos e ações", "Alimentação", "Território e natureza"}
FIELDS = {"bororo", "portugues", "tema", "publicar", "fonte_publica"}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("review_csv", type=Path, help="Planilha de revisão, NÃO adicionar ao Git")
    ap.add_argument("--output", type=Path, default=Path("docs/data/vocabulario-tematico-publico.json"))
    args = ap.parse_args()
    with args.review_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not FIELDS.issubset(reader.fieldnames or []):
            ap.error("Colunas necessárias: " + ", ".join(sorted(FIELDS)))
        rows = list(reader)
    result, seen = [], set()
    for line, row in enumerate(rows, 2):
        flag = (row.get("publicar") or "").strip().lower()
        if flag not in {"sim", "não", "nao", ""}:
            ap.error(f"Linha {line}: publicar deve ser sim ou não")
        if flag != "sim":
            continue
        bororo = (row.get("bororo") or "").strip()
        portugues = (row.get("portugues") or "").strip()
        tema = (row.get("tema") or "").strip()
        fonte = (row.get("fonte_publica") or "").strip()
        if not bororo or not portugues or tema not in THEMES or not fonte:
            ap.error(f"Linha {line}: entrada aprovada exige palavra, tradução, tema válido e fonte pública verificável")
        key = (bororo.casefold(), portugues.casefold(), tema)
        if key in seen:
            continue
        seen.add(key)
        result.append({"bororo": bororo, "portugues": portugues, "tema": tema})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(result)} entradas explicitamente aprovadas exportadas para {args.output}")

if __name__ == "__main__":
    main()
