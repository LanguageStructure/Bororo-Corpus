#!/usr/bin/env python3
"""Compare tokenizer hypotheses from two CoNLL-U versions without changing files.

Usage: python3 scripts/compare_tokenizer_models.py old.conllu new.conllu
Results are descriptive and are NOT a measure of linguistic accuracy.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from train_tokenizer import read_conllu, train


def compare(old_path, new_path, limit):
    old = train(read_conllu(old_path))
    new = train(read_conllu(new_path))
    old_c, new_c = old["candidates"], new["candidates"]
    old_forms, new_forms = set(old["lexicon"]), set(new["lexicon"])
    added = sorted(new_c.keys() - old_c.keys())
    removed = sorted(old_c.keys() - new_c.keys())
    changed = sorted(f for f in old_c.keys() & new_c.keys()
                     if old_c[f]["segments"] != new_c[f]["segments"])
    stable = len(old_c.keys() & new_c.keys()) - len(changed)
    print("COMPARAÇÃO DESCRITIVA — NÃO É MEDIDA DE ACURÁCIA")
    print(f"Anterior: {old_path.name}: {old['tokens']} tokens, {old['types']} tipos, {len(old_c)} candidatas")
    print(f"Nova:     {new_path.name}: {new['tokens']} tokens, {new['types']} tipos, {len(new_c)} candidatas")
    print(f"Formas novas: {len(new_forms - old_forms)}; ausentes: {len(old_forms - new_forms)}")
    print(f"Candidatas adicionadas: {len(added)}; removidas: {len(removed)}; "
          f"segmentações alteradas: {len(changed)}; estáveis: {stable}")
    for title, forms, models in [
        ("NOVAS CANDIDATAS", added, new_c),
        ("CANDIDATAS REMOVIDAS", removed, old_c),
    ]:
        print(f"\n{title} (até {limit}):")
        for form in forms[:limit]:
            print(f"  {form}: {' + '.join(models[form]['segments'])}")
    print(f"\nSEGMENTAÇÕES ALTERADAS (até {limit}):")
    for form in changed[:limit]:
        print(f"  {form}: {' + '.join(old_c[form]['segments'])}  ->  {' + '.join(new_c[form]['segments'])}")
    print("\nAviso: candidatas são hipóteses computacionais, não análises confirmadas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()
    compare(args.old, args.new, args.limit)
