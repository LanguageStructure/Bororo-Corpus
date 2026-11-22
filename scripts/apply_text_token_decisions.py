#!/usr/bin/env python3
"""Decisões de FFG (22/11/2026) sobre divergências entre o # text e os tokens.

1. "imedage" é o plural de "metuia": tokens "imetuia" onde o texto tem
   "imedage" passam a FORM imedage, Number=Plur (lema metuia mantido).
2. "paganure" e "peganure" existem; segue-se o texto: FORM peganure → paganure
   onde o texto tem paganure.
3. As formas separadas com "oino" estão corretas ("iro oino", não "iroino"):
   a) token fundido (iroino) onde o texto tem as duas palavras: o token é
      dividido em X + oino (com a elisão desfeita: iroino = iro + oino). X herda a anotação do token fundido (o lema vira X
      quando era cópia da forma fundida); "oino" recebe ADV/advmod ligado a X.
   b) texto fundido (roino) onde os tokens já estão separados: o # text recebe
      o espaço, e o texto original fica em "# text_source".

Decisões posteriores (22/11/2026):
4. "Barogwato" é sempre "barogwa to" ("Barogwatore" = "barogwa tore"): o token
   é dividido em barogwa (NOUN, obl) + to/tore (ADP, case), e o # text fundido
   recebe o espaço (original em # text_source).
5. "ref)" e "refl.)" no início de entradas do dicionário são erro: saem do
   # text (original em # text_source) e o token "ref)", se houver, é removido.
6. "Baadojeba" é a forma correta: onde o token é Baadojeba e o texto tem
   "Badojeba", corrige-se o # text.
7. "tagaregodure" é a forma correta: tokens "tagaaregodure" são corrigidos.

  python3 scripts/apply_text_token_decisions.py           # simulação
  python3 scripts/apply_text_token_decisions.py --apply   # grava e registra
"""
import argparse
import collections
import csv
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"


def set_feat(feats, k, v):
    d = {} if feats in ("_", "") else dict(f.split("=", 1) for f in feats.split("|") if "=" in f)
    d[k] = v
    return "|".join(f"{a}={d[a]}" for a in sorted(d, key=str.lower))


def renumber(rows, head_of_new):
    """rows: lista de (colunas, id_antigo ou None). HEADs apontam para IDs antigos,
    exceto os já resolvidos em head_of_new (índice da linha nova → índice da linha alvo)."""
    new = {}
    for n, (c, old) in enumerate(rows, 1):
        if old is not None and old not in new:
            new[old] = str(n)
    out = []
    for n, (c, old) in enumerate(rows, 1):
        c = list(c)
        c[0] = str(n)
        if n - 1 in head_of_new:
            c[6] = str(head_of_new[n - 1] + 1)
        elif c[6] not in ("_", "0"):
            c[6] = new.get(c[6], "_")
            if c[6] == "_":
                c[7] = "_"
        out.append(c)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    raw = CONLLU.read_text(encoding="utf-8").rstrip("\n").split("\n\n")
    log, stats = [], collections.Counter()
    for bi, block in enumerate(raw):
        lines = block.strip("\n").split("\n")
        com = [l for l in lines if l.startswith("#")]
        tok = [l.split("\t") for l in lines if l and not l.startswith("#")]
        if not tok or any(len(c) != 10 or not c[0].isdigit() for c in tok):
            continue
        sid = next((l.split("=", 1)[1].strip() for l in com if l.startswith("# sent_id")), "")
        ti = next((k for k, l in enumerate(com) if l.startswith("# text =")), None)
        if ti is None:
            continue
        text = com[ti].split("=", 1)[1].strip()
        words = re.findall(r"\w+", text)
        changed = False
        # 1 e 2: substituições de forma
        for c in tok:
            if c[1] == "imetuia" and "imedage" in words:
                log.append([sid, c[0], "imedage", "\t".join(c[1:6]), ""])
                c[1], c[5] = "imedage", set_feat(c[5], "Number", "Plur")
                log[-1][4] = "\t".join(c[1:6])
                stats["imedage"] += 1
                changed = True
            elif c[1].lower() == "peganure" and c[1].replace("e", "a", 1) in words:
                log.append([sid, c[0], "paganure", c[1], c[1].replace("e", "a", 1)])
                c[1] = c[1].replace("e", "a", 1)
                stats["paganure"] += 1
                changed = True
        # 3a: dividir tokens fundidos com oino
        rows, head_new = [], {}
        for c in tok:
            split = None
            if c[1] not in words:
                for mm in re.finditer(r"(?=oino)", c[1]):
                    k = mm.start()
                    # sem elisão (ako + oino = akooino) e com elisão do o (iro + oino = iroino)
                    for x, y in ((c[1][:k], c[1][k:]), (c[1][:k + 1], "o" + c[1][k + 1:])):
                        if x and re.search(rf"(?<!\w){re.escape(x)} {re.escape(y)}(?!\w)", text):
                            split = (x, y)
            if split:
                x, y = split
                cx = list(c)
                cx[1] = x
                if c[2].lower() == c[1].lower():
                    cx[2] = x.lower()
                cy = [c[0], y, "oino", "ADV", "adv", "_", "_", "advmod", "_",
                      "_" if y == "oino" else "AutoLowConf=Yes"]
                rows.append((cx, c[0]))
                head_new[len(rows)] = len(rows) - 1  # oino → X
                rows.append((cy, None))
                log.append([sid, c[0], "dividir_oino", c[1], f"{x} + {y}"])
                stats["dividir_oino"] += 1
            else:
                rows.append((c, c[0]))
        if len(rows) != len(tok):
            tok = renumber(rows, head_new)
            changed = True
        # 4: Barogwato / Barogwatore → barogwa + to / tore
        rows, head_new = [], {}
        for c in tok:
            m = re.fullmatch(r"([Bb]arogwa)(to(?:re)?)", c[1])
            if m:
                cx = list(c)
                cx[1], cx[2], cx[3], cx[4], cx[5], cx[7], cx[9] = m.group(1), "barogwa", "NOUN", "n", "_", \
                    (c[7] if c[7] in ("obl", "nsubj", "nmod", "root", "_") else "obl"), c[9]
                feats = "Number=Sing|Person=3" if m.group(2) == "to" else "Mood=Ind|Number=Sing|Person=3"
                cy = [c[0], m.group(2), "to", "ADP", "posp", feats, "_", "case", "_", "_"]
                rows.append((cx, c[0]))
                head_new[len(rows)] = len(rows) - 1
                rows.append((cy, None))
                log.append([sid, c[0], "dividir_barogwato", c[1], f"{m.group(1)} + {m.group(2)}"])
                stats["dividir_barogwato"] += 1
            else:
                rows.append((c, c[0]))
        if len(rows) != len(tok):
            tok = renumber(rows, head_new)
            changed = True
        # 5: token "ref)" sai
        if any(c[1] in ("ref)", "refl.)") for c in tok):
            rows = [(c, c[0]) for c in tok if c[1] not in ("ref)", "refl.)")]
            log.append([sid, "", "remover_token_ref", "ref)", ""])
            stats["remover_token_ref"] += 1
            tok = renumber(rows, {})
            changed = True
        # 7: tagaaregodure → tagaregodure
        for c in tok:
            if c[1].lower() == "tagaaregodure":
                log.append([sid, c[0], "tagaregodure", c[1], c[1][:4] + c[1][5:]])
                c[1] = c[1][:4] + c[1][5:]
                stats["tagaregodure"] += 1
                changed = True
        # 3b: texto fundido onde os tokens estão separados
        forms = [c[1] for c in tok]
        new_text = text
        for k in range(len(forms) - 1):
            if forms[k + 1] == "oino" and forms[k] != "oino":
                fused = forms[k] + ("ino" if forms[k].endswith("o") else "oino")  # elisão: ro + oino = roino
                n_tok = sum(1 for j in range(len(forms) - 1) if forms[j] == forms[k] and forms[j + 1] == "oino")
                n_sep = len(re.findall(rf"(?<!\w){re.escape(forms[k])} oino(?!\w)", new_text))
                if n_sep < n_tok and re.search(rf"(?<!\w){re.escape(fused)}(?!\w)", new_text):
                    new_text = re.sub(rf"(?<!\w){re.escape(fused)}(?!\w)", f"{forms[k]} oino", new_text, count=1)
                    log.append([sid, "", "texto_separar_oino", fused, f"{forms[k]} oino"])
                    stats["texto_separar_oino"] += 1
        for k in range(len(forms) - 1):  # 4: Barogwato no texto
            if forms[k].lower() == "barogwa" and forms[k + 1] in ("to", "tore"):
                fused = forms[k] + forms[k + 1]
                if re.search(rf"(?<!\w){fused}(?!\w)", new_text):
                    new_text = re.sub(rf"(?<!\w){fused}(?!\w)", f"{forms[k]} {forms[k + 1]}", new_text, count=1)
                    log.append([sid, "", "texto_separar_barogwato", fused, f"{forms[k]} {forms[k + 1]}"])
                    stats["texto_separar_barogwato"] += 1
        m = re.match(r"^refl?\.?\)\s*", new_text)  # 5
        if m:
            new_text = new_text[m.end():]
            log.append([sid, "", "texto_remover_ref", m.group(0).strip(), ""])
            stats["texto_remover_ref"] += 1
        if "Baadojeba" in " ".join(forms) and re.search(r"(?<!\w)Badojeba", new_text):  # 6
            new_text = re.sub(r"(?<!\w)Badojeba", "Baadojeba", new_text)
            log.append([sid, "", "texto_baadojeba", "Badojeba", "Baadojeba"])
            stats["texto_baadojeba"] += 1
        if new_text != text:
            com[ti] = f"# text = {new_text}"
            if not any(l.startswith("# text_source") for l in com):
                com.insert(ti + 1, f"# text_source = {text}")
            changed = True
        if changed:
            raw[bi] = "\n".join(com + ["\t".join(c) for c in tok])
    print(dict(stats))
    if a.apply:
        CONLLU.write_text("\n\n".join(raw) + "\n\n", encoding="utf-8")
        p = ROOT / f"CorBo/validation/text_token_decisions_{date.today():%Y%m%d}.tsv"
        new_file = not p.exists()
        with p.open("a", encoding="utf-8", newline="") as fh:  # rodadas do mesmo dia se acumulam
            w = csv.writer(fh, delimiter="\t")
            if new_file:
                w.writerow(["sent_id", "token", "kind", "before", "after"])
            w.writerows(log)
        print("registro:", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
