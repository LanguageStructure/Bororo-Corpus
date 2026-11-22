#!/usr/bin/env python3
"""Aplica as propostas aprovadas de CorBo/validation/structural_proposals.tsv.

Só as linhas com approve = "sim" são aplicadas (tipos merge, new_sentence,
renumber). Gere as propostas novamente se o CoNLL-U tiver mudado desde então:
as linhas são localizadas pelo número de linha do arquivo.

  python3 scripts/apply_structural_fixes.py            # simulação: mostra o que faria
  python3 scripts/apply_structural_fixes.py --apply    # grava no CorBo.conllu
Depois: validate_conllu.py, split_gold_silver.py e atualizar a linha de base.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from propose_structural_fixes import CONLLU, OUT, info, parse_blocks  # noqa: E402


def renumber(parts):
    """parts: lista de listas de linhas de token (cada parte com sua numeração original).
    Renumera 1..n; HEAD é resolvido primeiro na própria parte, depois nas anteriores."""
    maps, out, new = [], [], 0
    for part in parts:
        m = {}
        for cols in part:
            if re.fullmatch(r"\d+", cols[0]):
                new += 1
                m[cols[0]] = str(new)
        maps.append(m)
    for k, part in enumerate(parts):
        for cols in part:
            c = list(cols)
            if not re.fullmatch(r"\d+", c[0]):
                continue  # multi-palavra / vazios: não ocorrem nestes casos
            c[0] = maps[k][cols[0]]
            if c[6] not in ("_", "0"):
                target = maps[k].get(c[6]) or next((maps[j][c[6]] for j in range(k - 1, -1, -1) if c[6] in maps[j]), None)
                c[6] = target or "_"
                if target is None:
                    c[7] = "_"
            out.append("\t".join(c))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    approved = {}
    with OUT.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r.get("approve", "").strip().lower() in ("sim", "s", "yes", "y", "x"):
                approved[int(r["line"])] = r
    if not approved:
        raise SystemExit("Nenhuma proposta aprovada (coluna approve = sim).")

    blocks = parse_blocks(CONLLU.read_text(encoding="utf-8"))
    out = []   # cada item: {"comments": [...], "parts": [[cols...]], "renumber": bool}
    done = {}
    for line, lines in blocks:
        sid, text, tok = info(lines)
        com = [l for l in lines if l.startswith("#")]
        r = approved.get(line)
        if r and r["kind"] == "merge" and out:
            target = next((o for o in reversed(out) if any(re.match(r"#\s*sent_id\s*=", c) for c in o["comments"])), None)
            if target:
                target["parts"].append(tok)
                target["renumber"] = True
                target["raw"] = None
                done[r["prop_id"]] = f"unido a {target['sid']}"
                continue
        if r and r["kind"] == "new_sentence":
            new_id = re.search(r"criar sentença (\S+)", r["proposal"]).group(1)
            com = [f"# sent_id = {new_id}", "# text = " + " ".join(t[1] for t in tok),
                   "# text_note = reconstruído a partir das formas (fragmento separado da sentença anterior)"] + com
            out.append({"comments": com, "parts": [tok], "renumber": True, "sid": new_id})
            done[r["prop_id"]] = f"nova sentença {new_id}"
            continue
        out.append({"comments": com, "parts": [tok], "renumber": bool(r and r["kind"] == "renumber"), "sid": sid,
                    "raw": None if r else lines})
        if r and r["kind"] == "renumber":
            done[r["prop_id"]] = f"renumerada {sid}"

    text = []
    for o in out:
        if o.get("raw") is not None and not o["renumber"]:
            text.append("\n".join(o["raw"]))  # bloco intocado: preservado exatamente
            continue
        toks = renumber(o["parts"]) if o["renumber"] else ["\t".join(c) for p in o["parts"] for c in p]
        text.append("\n".join(o["comments"] + toks))
    result = "\n\n".join(t for t in text if t.strip()) + "\n\n"
    missing = set(r["prop_id"] for r in approved.values()) - set(done)
    print(f"{len(done)} propostas aplicáveis; {len(missing)} não localizadas: {sorted(missing)[:10]}")
    for k in list(done)[:15]:
        print(" ", k, done[k])
    if args.apply:
        CONLLU.write_text(result, encoding="utf-8")
        print("Gravado:", CONLLU.relative_to(ROOT))
    else:
        print("Simulação (use --apply para gravar).")


if __name__ == "__main__":
    main()
