#!/usr/bin/env python3
"""Prepara os arquivos para download e o manifesto lido pela página Downloads.

Gera:
  docs/downloads/corbo-parallel.tsv   todas as unidades documentais publicadas
                                      (id, coleção, estado, Bororo, português)
  docs/data/downloads.json            manifesto: arquivo, formato, tamanho,
                                      contagens e descrição em PT/EN
Arquivos fora de docs/ (CoNLL-U, camadas gold/silver) são apontados no
GitHub (ramo main), que é de onde o site publicado é servido.
"""
import csv
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RAW = "https://raw.githubusercontent.com/LanguageStructure/Bororo-Corpus/main/"
BLOB = "https://github.com/LanguageStructure/Bororo-Corpus/blob/main/"


def count_conllu(path):
    s = t = 0
    for line in path.read_text(encoding="utf-8").split("\n"):
        if re.match(r"#\s*sent_id\s*=", line):
            s += 1
        elif re.match(r"\d+\t", line):
            t += 1
    return s, t


def main():
    units = json.loads((DOCS / "data/corbo-units.json").read_text(encoding="utf-8"))
    out_dir = DOCS / "downloads"
    out_dir.mkdir(exist_ok=True)
    # Unidades com licença própria (ex.: Pao Kurirewu Bataru Kurirewu, CC BY-NC-ND 4.0) ficam fora do arquivo
    # geral, que é CC BY 4.0, e vão para arquivos separados com a licença no nome da descrição.
    third = [u for u in units if u.get("license")]
    units = [u for u in units if not u.get("license")]
    pkb = [u for u in third if u.get("collection") == "Pao Kurirewu Bataru Kurirewu"]
    if pkb:
        with (out_dir / "pao-kurirewu-bataru.tsv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t", lineterminator="\n")
            w.writerow(["id", "book", "chapter", "verse", "bororo", "license"])
            for u in pkb:
                w.writerow([u["id"], u.get("book", ""), u.get("chapter", ""), u.get("verse", ""), " ".join(str(u.get("b") or "").split()), u["license"]])
    par = out_dir / "corbo-parallel.tsv"
    with par.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["id", "collection", "status", "bororo", "portuguese"])
        for u in units:
            clean = lambda x: " ".join(str(x or "").split())
            w.writerow([u.get("id", ""), u.get("collection", ""), u.get("status", ""), clean(u.get("b")), clean(u.get("p"))])
    with_pt = sum(1 for u in units if (u.get("p") or "").strip())

    items = []

    def add(group, path, url, fmt, pt, en, counts_pt="", counts_en=""):
        p = ROOT / path
        items.append({"group": group, "name": Path(path).name, "path": path, "url": url, "format": fmt,
                      "bytes": p.stat().st_size if p.exists() else None, "pt": pt, "en": en,
                      "counts_pt": counts_pt, "counts_en": counts_en})

    add("textos", "docs/downloads/corbo-parallel.tsv", "downloads/corbo-parallel.tsv", "TSV (UTF-8)",
        "Todas as unidades documentais publicadas, com coleção, estado editorial, texto Bororo e tradução portuguesa quando existe.",
        "All published documentary units, with collection, editorial status, Bororo text and Portuguese translation when available.",
        f"{len(units):,} unidades · {with_pt:,} com tradução".replace(",", "."),
        f"{len(units):,} units · {with_pt:,} with translation")
    if pkb:
        add("textos", "docs/downloads/pao-kurirewu-bataru.tsv", "downloads/pao-kurirewu-bataru.tsv", "TSV (UTF-8)",
            "Novo Testamento Pao Kurirewu Bataru Kurirewu (© 2019 Wycliffe Bible Translators), ortografia adaptada ao CorBo. "
            "Licença própria: CC BY-NC-ND 4.0 (uso não comercial), não CC BY 4.0.",
            "New Testament Pao Kurirewu Bataru Kurirewu (© 2019 Wycliffe Bible Translators), orthography adapted to CorBo. "
            "Separate license: CC BY-NC-ND 4.0 (non-commercial), not CC BY 4.0.",
            f"{len(pkb):,} unidades".replace(",", "."), f"{len(pkb):,} units")
    canon = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
    s, t = count_conllu(canon)
    add("anotacao", "CorBo/Corpus_Files/CorBo.conllu", RAW + "CorBo/Corpus_Files/CorBo.conllu", "CoNLL-U",
        "Arquivo canônico de anotação (lemas, classes, traços, dependências), incluindo anotação automática marcada com Auto=.",
        "Canonical annotation file (lemmas, POS, features, dependencies), including automatic annotation marked with Auto=.",
        f"{s:,} sentenças · {t:,} tokens".replace(",", "."), f"{s:,} sentences · {t:,} tokens")
    for name, pt, en in [("CorBo.gold.conllu", "Camada gold: só anotação manual, sintaxe completa, sem erros estruturais.",
                          "Gold layer: manual annotation only, complete syntax, no structural errors."),
                         ("CorBo.silver.conllu", "Camada silver: estruturalmente válida, com anotação automática.",
                          "Silver layer: structurally valid, includes automatic annotation.")]:
        path = f"CorBo/Corpus_Files/splits/{name}"
        if (ROOT / path).exists():
            s, t = count_conllu(ROOT / path)
            add("anotacao", path, RAW + path, "CoNLL-U", pt, en, f"{s:,} sentenças · {t:,} tokens".replace(",", "."),
                f"{s:,} sentences · {t:,} tokens")
    add("anotacao", "CorBo/Corpus_Files/splits/review_sentences.tsv", RAW + "CorBo/Corpus_Files/splits/review_sentences.tsv", "TSV",
        "Sentenças que aguardam revisão, com o motivo.", "Sentences awaiting review, with the reason.")
    add("lexico", "docs/data/dicionario-bororo-publico.json", "data/dicionario-bororo-publico.json", "JSON",
        "Entradas publicadas do Dicionário Bororo (forma, IPA, classe, definição, exemplo).",
        "Published Bororo Dictionary entries (form, IPA, class, definition, example).")
    add("lexico", "docs/data/tokenizer-v5-site.json", "data/tokenizer-v5-site.json", "JSON",
        "Inventário do tokenizador: segmentações confirmadas e propostas, estado de revisão, superfície e representação subjacente.",
        "Tokenizer inventory: confirmed and proposed segmentations, review status, surface and underlying representation.")
    add("lexico", "docs/data/statistics-summary.json", "data/statistics-summary.json", "JSON",
        "Resumo estatístico: tokens por coleção, classes gramaticais, totais.",
        "Statistical summary: tokens per collection, parts of speech, totals.")
    add("documentacao", "docs/ANNOTATION_GUIDE.md", BLOB + "docs/ANNOTATION_GUIDE.md", "Markdown",
        "Guia de anotação do CoNLL-U.", "CoNLL-U annotation guide (Portuguese).")
    add("documentacao", "docs/citation.bib", "citation.bib", "BibTeX", "Referência para citação.", "Citation reference.")

    manifest = {"generated": date.today().isoformat(), "license": "CC BY 4.0",
                "doi": "10.5281/zenodo.23441622",
                "repository_zip": "https://github.com/LanguageStructure/Bororo-Corpus/archive/refs/heads/main.zip",
                "files": items}
    (DOCS / "data/downloads.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} arquivos no manifesto; corbo-parallel.tsv com {len(units)} unidades")


if __name__ == "__main__":
    main()
