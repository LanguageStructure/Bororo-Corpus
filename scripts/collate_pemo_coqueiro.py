#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Colação focalizada de um intervalo de Pemo–Coqueiro contra a História Mítica.

Substitui os antigos collate_pemo_coqueiro_001_039.py, _040_079, _080_119,
_120_159, _160_183, _190_223 e _257_274, que diferiam apenas no intervalo.
Diagnóstico somente; não grava nada.

Exemplos:
  python3 scripts/collate_pemo_coqueiro.py 1 39
  python3 scripts/collate_pemo_coqueiro.py 257 274 --threshold 0.7
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PC = ROOT / "CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"
PUB = ROOT / "docs/data/corbo-units.json"


def norm(s):
    s = unicodedata.normalize("NFC", str(s or "")).casefold()
    s = re.sub(r"[^a-záéíóúâêôãõçüñ]+", " ", s)
    return " ".join(s.split())


def sim(a, b):
    a, b = norm(a), norm(b)
    return SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0.0


def num(s):
    m = re.search(r"(\d+)$", str(s or ""))
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("start", type=int, help="primeiro número de unidade PC (inclusive)")
    ap.add_argument("end", type=int, help="último número de unidade PC (inclusive)")
    ap.add_argument("--top", type=int, default=3, help="candidatos por unidade (padrão: 3)")
    ap.add_argument("--threshold", type=float, default=0.70, help="limiar para listar âncoras (padrão: 0.70)")
    args = ap.parse_args()

    with PC.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t")
                if num(r["id"]) is not None and args.start <= num(r["id"]) <= args.end]
    raw = json.loads(PUB.read_text(encoding="utf-8"))
    units = raw if isinstance(raw, list) else raw.get("units", [])
    hm = {}
    for u in units:
        m = re.search(r"HM001-u(\d+)$", str(u.get("id", "")))
        if m:
            hm[int(m.group(1))] = u
    windows = []
    for start in sorted(hm):
        for width in (1, 2, 3):
            ns = list(range(start, start + width))
            if all(x in hm for x in ns):
                b = " ".join(str(hm[x].get("b") or hm[x].get("source") or "") for x in ns)
                p = " ".join(str(hm[x].get("p") or hm[x].get("portuguese") or hm[x].get("translation_pt") or "") for x in ns)
                windows.append((ns, b, p))

    print(f"PEMO–COQUEIRO PC.{args.start:03d}–{args.end:03d} × HISTÓRIA MÍTICA")
    print(f"Top {args.top} candidatos; diagnóstico somente.\n")
    anchors = []
    for r in rows:
        src = r.get("reviewed") or r.get("source") or ""
        scores = sorted(((sim(src, b), ns, b, p) for ns, b, p in windows), reverse=True, key=lambda z: z[0])[:args.top]
        if scores and scores[0][0] >= args.threshold:
            anchors.append((r["id"], scores[0][1], scores[0][0]))
        print("=" * 104)
        print(f"{r['id']} | BOR: {src}")
        print(f"PT: {r.get('portuguese', '')}")
        for rank, (s, ns, b, p) in enumerate(scores, 1):
            ids = "+".join(f"u{x:03d}" for x in ns)
            print(f"  {rank}. HM {ids} [{s:.3f}]")
            print(f"     BOR: {b}")
            if p:
                print(f"     PT : {p}")
    print("\n" + "#" * 104)
    print(f"ÂNCORAS >= {args.threshold:.2f} (não são confirmação automática)")
    for pid, ns, s in anchors:
        print(f"{pid} => " + "+".join(f"u{x:03d}" for x in ns) + f" [{s:.3f}]")


if __name__ == "__main__":
    main()
