import argparse
import json
import sys
from dataclasses import asdict

from . import Tokenizer


def main():
    ap = argparse.ArgumentParser(prog="corbo-tokenize", description="Tokenizador do Bororo (CorBo)")
    ap.add_argument("text", nargs="?", help="texto (se omitido, lê da entrada padrão)")
    ap.add_argument("--format", choices=["text", "tsv", "json", "conllu"], default="text")
    ap.add_argument("--inventory", help="caminho para tokenizer-v5-site.json")
    a = ap.parse_args()
    text = a.text if a.text is not None else sys.stdin.read()
    tk = Tokenizer(a.inventory)
    if a.format == "conllu":
        sys.stdout.write("".join(tk.to_conllu(line) for line in text.splitlines() if line.strip()))
        return
    toks = tk.analyze(text)
    if a.format == "json":
        print(json.dumps([asdict(t) for t in toks], ensure_ascii=False, indent=1))
    elif a.format == "tsv":
        print("form\tsegments\tunderlying\tstatus")
        for t in toks:
            print(f"{t.form}\t{'+'.join(t.segments)}\t{'+'.join(t.underlying)}\t{t.status}")
    else:
        print(" ".join("+".join(t.segments) if t.segments else t.form for t in toks))


if __name__ == "__main__":
    main()
