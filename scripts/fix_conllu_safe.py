#!/usr/bin/env python3
"""Correções automáticas *seguras* no CoNLL-U do CorBo.

Só aplica correções sem ambiguidade linguística (erros de digitação de rótulos,
normalização de grafia de valores, colunas trocadas inequívocas, cabeçalhos de
sentença separados por linha em branco). Tudo o que exige decisão humana
(ciclos, raízes múltiplas, texto ≠ formas, IDs não sequenciais, fragmentos) é
deixado intacto e aparece no relatório de scripts/validate_conllu.py.

Cada alteração é registrada em um TSV (linha original, sent_id, coluna, antes,
depois, regra). Por padrão roda em modo de simulação; use --apply para gravar.

  python3 scripts/fix_conllu_safe.py CorBo/Corpus_Files/CorBo.conllu \
      --log CorBo/validation/safe_fixes.tsv            # simulação
  python3 scripts/fix_conllu_safe.py CorBo/Corpus_Files/CorBo.conllu \
      --log CorBo/validation/safe_fixes.tsv --apply    # grava no próprio arquivo
"""
import argparse
import collections
import csv
import re
from pathlib import Path

UD_UPOS = set("ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X".split())

# Chaves de FEATS com erro de digitação evidente.
FEAT_KEY_FIX = {
    "Perdson": "Person", "Persoon": "Person", "Person?": "Person", "Rfelex": "Reflex",
    "Numner": "Number", "Voica": "Voice", "PronTYpe": "PronType", "Dexis": "Deixis",
    "Clusivit": "Clusivity", "_Mood": "Mood", "ood": "Mood",
}
# Valores com grafia inconsistente (mesma categoria, caixa ou letra trocada).
FEAT_VALUE_FIX = {
    ("Clusivity", "EX"): "Ex", ("Mood", "ind"): "Ind", ("Mood", "imp"): "Imp",
    ("Status", "irr"): "Irr", ("Number", "sing"): "Sing", ("Number", "SIng"): "Sing",
    ("Number", "Sinf"): "Sing", ("Voice", "Pas"): "Pass", ("Person", "3_"): "3",
    ("Person", "3 n"): "3", ("Reflex", "Ye"): "Yes", ("Reflex", "Yex"): "Yes",
}
# XPOS: variantes de caixa/espaço/digitação do mesmo rótulo do projeto.
XPOS_FIX = {
    " vt": "vt", "psp": "posp", "psop": "posp", "punc": "punct", "N": "n", "V": "v", "v7": "v",
    "NOUN": "n", "noun": "n", "PROPN": "propn", "X": "x", "SCONJ": "sconj", "VERB": "v",
}
# Dois traços colados sem "|" (ex.: Mood=IndNumber=Plur).
GLUED = re.compile(r"^([A-Z][A-Za-z\[\]a-z]*)=([A-Za-z0-9]+?)([A-Z][a-z]+=.+)$")
KNOWN_KEYS = {"Number", "Person", "Mood", "Polarity", "Voice", "Clusivity", "Reflex", "Aspect", "Deixis"}

DEPREL_FIX = {
    "disocurse": "discourse", "advmo": "advmod", "nubj": "nsubj", "nsubhj": "nsubj",
    "subj": "nsubj", "obk": "obj", "falt": "flat", "voc": "vocative", "adv": "advmod",
    "roos": "root", "roo": "root", "prataxis": "parataxis", "nusbj": "nsubj", "nubsj": "nsubj",
    "ccoomp": "ccomp", "ccompo": "ccomp", "advmoa": "advmod", "advod": "advmod",
}
# Glosas em português que vazaram para MISC sem chave.
GLOSS_LIKE = re.compile(r"^[a-zà-ú][a-zà-ú ,]+$")


def sort_feats(items):
    # UD: ordem alfabética das chaves, sem diferenciar maiúsculas.
    return sorted(items, key=lambda kv: kv.split("=", 1)[0].lower())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("conllu")
    ap.add_argument("--log", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    path = Path(args.conllu)
    raw = path.read_text(encoding="utf-8")
    lines = raw.split("\n")
    log = []

    # XPOS → UPOS majoritário (para corrigir UPOS ausente ou com o lema copiado).
    xu = collections.defaultdict(collections.Counter)
    for l in lines:
        f = l.split("\t")
        if len(f) == 10 and f[3] in UD_UPOS and f[4] != "_":
            xu[f[4]][f[3]] += 1
    xpos_to_upos = {}
    for x, c in xu.items():
        top, n = c.most_common(1)[0]
        if n / sum(c.values()) >= 0.98 and n >= 20:  # só mapeamentos praticamente unívocos
            xpos_to_upos[x] = top

    sid = ""
    out = []
    for i, l in enumerate(lines, 1):
        m = re.match(r"#\s*sent_id\s*=\s*(.*)$", l)
        if m:
            sid = m.group(1)
        f = l.split("\t")
        if l.startswith("#") or len(f) != 10:
            out.append(l)
            continue

        def change(col, old, new, rule):
            log.append({"line": i, "sent_id": sid, "column": col, "before": old, "after": new, "rule": rule})

        # 1. Espaços nas bordas de FORM/LEMMA.
        for idx, col in ((1, "FORM"), (2, "LEMMA")):
            if f[idx] != f[idx].strip() and f[idx].strip():
                change(col, f[idx], f[idx].strip(), "strip_whitespace")
                f[idx] = f[idx].strip()

        # 2. Colunas deslocadas (lema repetido na coluna UPOS e UPOS na coluna XPOS).
        if f[3] == f[2] and f[4] in UD_UPOS and f[3] not in UD_UPOS and re.fullmatch(r"\d+", f[6]) and f[7] != "_" and f[8] == "_":
            old = "\t".join(f)
            # 10 baru baru baru NOUN n 11 nmod _ _ → 10 baru baru NOUN n _ 11 nmod _ _
            f = [f[0], f[1], f[2], f[4], f[5], "_", f[6], f[7], "_", f[9]]
            change("ROW", old, "\t".join(f), "column_shift_lemma_in_upos")
        elif f[3] == f[2] and f[4] in UD_UPOS and f[3] not in UD_UPOS and "=" in f[6]:
            old = "\t".join(f)
            # 12 bu bu bu VERB vt Feats _ _ _ → 12 bu bu VERB vt Feats _ _ _ _
            f = [f[0], f[1], f[2], f[4], f[5], f[6], f[7], f[8], "_", f[9]]
            change("ROW", old, "\t".join(f), "column_shift_lemma_in_upos")
        elif f[2] in UD_UPOS and f[3] == f[4] and f[3] not in UD_UPOS:
            old = "\t".join(f)
            # 3 paro NOUN n n Feats … → 3 paro _ NOUN n Feats … (lema desconhecido)
            f = [f[0], f[1], "_", f[2], f[4]] + f[5:]
            change("ROW", old, "\t".join(f), "column_shift_upos_in_lemma")

        # 3. UPOS: espaços, lema copiado para UPOS, UPOS ausente com XPOS unívoco.
        if f[3].strip() in UD_UPOS and f[3] != f[3].strip():
            change("UPOS", f[3], f[3].strip(), "strip_whitespace")
            f[3] = f[3].strip()
        if f[3] not in UD_UPOS and f[4] in xpos_to_upos and (f[3] == "_" or f[3] == f[2]):
            new = xpos_to_upos[f[4]]
            change("UPOS", f[3], new, "upos_from_unambiguous_xpos")
            f[3] = new
            if f[9] != "_" and "Auto=" in f[9]:
                f[9] = re.sub(r"Auto=([^|]*)", lambda mm: "Auto=" + "+".join(dict.fromkeys(mm.group(1).split("+") + ["upos"])), f[9])
            else:
                f[9] = ("Auto=upos" if f[9] == "_" else f[9] + "|Auto=upos")
        # Também para XPOS sconj/adv: o mapeamento majoritário já resolve dukeje.

        # 3b. XPOS.
        if f[4] in XPOS_FIX:
            change("XPOS", f[4], XPOS_FIX[f[4]], "xpos_variant")
            f[4] = XPOS_FIX[f[4]]
        elif "=" in f[4] and f[5] == "_" and f[3] == "DET":
            change("ROW", f[4], "XPOS=art; FEATS=" + f[4], "feats_in_xpos")
            f[5], f[4] = "|".join(sort_feats(f[4].split("|"))), "art"

        # 4. FEATS.
        if f[5] != "_":
            old = f[5]
            items = []
            for kv in f[5].split("|"):
                if kv == "" or kv.lower() == f[4].lower() or kv in ("propn", "n", "x", "vt", "aux"):
                    continue  # vazio ou XPOS que vazou para FEATS
                g = GLUED.match(kv)
                if g and g.group(1) in KNOWN_KEYS:
                    tail_key = g.group(3).split("=")[0]
                    if tail_key in KNOWN_KEYS:
                        items += [f"{g.group(1)}={g.group(2)}", g.group(3)]
                        continue
                mm = re.fullmatch(r"(Mood|Person|Number)(Opt|Ind|Imp|Sub|[123])", kv)
                if mm:  # MoodOpt → Mood=Opt, Person3 → Person=3
                    kv = f"{mm.group(1)}={mm.group(2)}"
                if "=" not in kv:
                    items.append(kv)
                    continue
                k, v = kv.split("=", 1)
                k = FEAT_KEY_FIX.get(k, k)
                mm = re.fullmatch(r"([A-Za-z0-9]+)\[(psor|abs|erg)\]", v)
                if mm:  # Person=1[psor] → Person[psor]=1
                    k, v = f"{k}[{mm.group(2)}]", mm.group(1)
                v = FEAT_VALUE_FIX.get((k, v), v)
                if v == "":
                    continue  # traço sem valor não carrega informação
                items.append(f"{k}={v}")
            # Valor impossível na chave errada: Number=3 → Person=3; Person=Sing → Number=Sing
            keys = [x.split("=", 1)[0] for x in items]
            for a, b, vals in (("Number", "Person", {"1", "2", "3"}), ("Person", "Number", {"Sing", "Plur"})):
                bad = [x for x in items if x.split("=", 1)[0] == a and x.split("=", 1)[1] in vals]
                if bad and b not in keys:
                    items = [f"{b}={x.split('=', 1)[1]}" if x in bad else x for x in items]
                elif bad and f"{b}=" + bad[0].split("=", 1)[1] in items:
                    items = [x for x in items if x not in bad]  # duplicata de informação já presente
            # remove duplicatas exatas, ordena
            items = sort_feats(list(dict.fromkeys(items)))
            new = "|".join(items) if items else "_"
            if new != old:
                change("FEATS", old, new, "feats_normalize")
                f[5] = new

        # 5. DEPREL.
        if f[7] != f[7].strip() and f[7].strip():
            change("DEPREL", f[7], f[7].strip(), "strip_whitespace")
            f[7] = f[7].strip()
        if f[7] in DEPREL_FIX:
            change("DEPREL", f[7], DEPREL_FIX[f[7]], "deprel_typo")
            f[7] = DEPREL_FIX[f[7]]

        # 6. MISC.
        if f[9] != "_":
            old = f[9]
            items = []
            for it in f[9].split("|"):
                if it in ("_", ""):
                    continue
                if "=" not in it and GLOSS_LIKE.match(it):
                    items.append("Gloss=" + it.replace(" ", "_"))
                    continue
                items.append(it)
            new = "|".join(items) if items else "_"
            if new != old:
                change("MISC", old, new, "misc_normalize")
                f[9] = new

        out.append("\t".join(f))

    # 7. Cabeçalhos separados por linha em branco: um bloco só de comentários,
    #    sem "# text =" vazio, pertence ao bloco seguinte (que não tem sent_id).
    text = "\n".join(out)
    blocks = text.split("\n\n")
    merged = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        bl = [x for x in b.split("\n") if x != ""]
        is_header = bl and all(x.startswith("#") for x in bl) and not re.search(r"^# text =\s*$", b, re.M)
        orphan = is_header and not any(re.match(r"#\s*(sent_id|text)\s*=", x) for x in bl)
        if orphan and i + 1 < len(blocks) and blocks[i + 1].strip():
            # comentário solto (ex.: model_projection) pertence à sentença seguinte
            blocks[i + 1] = b.rstrip("\n") + "\n" + blocks[i + 1].lstrip("\n")
            log.append({"line": "", "sent_id": bl[0][:60], "column": "BLOCK", "before": "comentário solto",
                        "after": "unido ao bloco seguinte", "rule": "merge_orphan_comment"})
            i += 1
            continue
        if is_header and i + 1 < len(blocks):
            nxt = blocks[i + 1]
            nl = [x for x in nxt.split("\n") if x != ""]
            if nl and not any(re.match(r"#\s*sent_id\s*=", x) for x in nl) and not (
                    any(re.match(r"#\s*text\s*=", x) for x in bl) and any(re.match(r"#\s*text\s*=", x) for x in nl)):
                blocks[i + 1] = b.rstrip("\n") + "\n" + nxt.lstrip("\n")
                log.append({"line": "", "sent_id": bl[0][:60], "column": "BLOCK", "before": "cabeçalho separado",
                            "after": "unido ao bloco seguinte", "rule": "merge_split_header"})
                i += 1
                continue
        merged.append(b)
        i += 1
    text = "\n\n".join(merged)

    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    with open(args.log, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ["line", "sent_id", "column", "before", "after", "rule"], delimiter="\t")
        w.writeheader()
        w.writerows(log)
    counts = collections.Counter(x["rule"] for x in log)
    print(f"{len(log)} alterações:", dict(counts))
    print("XPOS→UPOS usados:", xpos_to_upos)
    if args.apply:
        path.write_text(text, encoding="utf-8")
        print("Gravado:", path)
    else:
        print("Simulação (use --apply para gravar).")


if __name__ == "__main__":
    main()
