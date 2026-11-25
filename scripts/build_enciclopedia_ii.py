#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enciclopédia Bororo, vol. II (Lendas): da transcrição marcada às tabelas da coleção.

Entrada:  CorBo_vNext/texts/enciclopedia-bororo-ii/transcricao/lendaNN.txt
Saída (na pasta da coleção):
  enciclopedia_ii_parallel.tsv      uma linha por frase: bororo (ortografia do CorBo) + tradução numerada
  enciclopedia_ii_interlinear.tsv   pares palavra/glosa por célula do original (forma impressa e normalizada)
  enciclopedia_ii_notas.tsv         notas de rodapé, com as frases que as chamam
  enciclopedia_ii_editorial.tsv     introdução, narrativa, variantes em prosa, cabeçalhos, legendas de fotos
  enciclopedia_ii_normalizacao.tsv  forma normalizada x impressa, ocorrências e se é atestada no CorBo
  enciclopedia_ii_lendaNN_paralelo.txt  linha bororo / linha portuguesa, como os *_paralelo.txt do corpus

Convenções (decisões de FFG, 25/11/2026):
  * o bororo é transcrito sem acentos e sem diacríticos subscritos (feito na própria transcrição);
  * texto paralelo = frase bororo + tradução numerada da Enciclopédia (não as glosas);
  * sem hífens e sem apóstrofos;
  * -u depois de vogal = sufixo -wu (Kujagureu > Kujagurewu);
  * nure e rogu se ligam à palavra anterior (Boe nure > Boenure; nogedu rogu > nogedurogu).
A forma impressa (com hífens) fica preservada na coluna `source`.

Marcação da transcrição: @lenda N, @titulo, @pagina N, @intro, @narrativa,
@variante RÓTULO | NOTA, @texto TÍTULO BORORO | TÍTULO PT, @secao RÓTULO | NOTA,
@s N (frase), "bororo | glosa" (uma célula por linha; "(n)" = chamada de nota),
@titulo_trad, @secao_trad, @t N tradução, @n N nota, @foto legenda, @ciclo título de ciclo, @@ (fim de bloco).

Uso: python scripts/build_enciclopedia_ii.py [--check]
  --check  só confere a transcrição e mostra o resumo, sem gravar.
"""
from __future__ import annotations
import csv, glob, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COL = ROOT / 'CorBo_vNext/texts/enciclopedia-bororo-ii'
SRC = COL / 'transcricao'
PREFIX = 'BOR-CORBO-ENC2'
COLLECTION = 'Enciclopédia Bororo II'

NOTE = re.compile(r'\s*\((\d+)\)?')          # "(12)"; aceita "(12" sem fechar, como impresso
VOWEL_U = re.compile(r'([aeio])u$', re.I)
WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*[A-Za-z]|[A-Za-z]")


def norm_word(w: str) -> str:
    core = w.replace('-', '').replace("'", '')
    return VOWEL_U.sub(r'\1wu', core)


# Formas que se escrevem ligadas à palavra anterior (decisão de FFG, 25/11/2026).
BOUND = {'nure', 'rogu'}
BOUND_IN = re.compile(r"([A-Za-z])\s+(" + '|'.join(sorted(BOUND)) + r")\b")


def norm_text(t: str) -> str:
    return BOUND_IN.sub(r'\1\2', WORD.sub(lambda m: norm_word(m.group(0)), t))


def is_bound(cell_norm: str) -> bool:
    return cell_norm.strip('.,;:!?"…').lower() in BOUND


def join_cells(cs) -> str:
    """Texto da frase a partir das células normalizadas: nure/rogu colados à célula anterior,
    desde que ela não termine em pontuação (casos assim vão para o relatório)."""
    out = ''
    for c in cs:
        out = out + c['bororo_norm'] if c.get('ligada') else (out + ' ' + c['bororo_norm']).strip()
    return out


def parse(path: Path):
    L = dict(lenda=None, titulo='', texto_titulo='', trad_titulo='')
    ed, cells, trans, notes = [], [], {}, {}
    page = None; mode = None; sec = 'Texto principal'; sent = None; cell_i = 0; ordem = 0; vlabel = ''

    def add_ed(tipo, txt, rotulo=''):
        nonlocal ordem
        ordem += 1
        ed.append(dict(lenda=L['lenda'], ordem=ordem, tipo=tipo, rotulo=rotulo, pagina=page, texto=txt))

    for n_line, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith('@@'):
            mode = None
            continue
        if line.startswith('@'):
            key, _, val = line[1:].partition(' ')
            if key == 'lenda': L['lenda'] = int(val)
            elif key == 'titulo': L['titulo'] = val
            elif key == 'pagina': page = int(val)
            elif key in ('intro', 'narrativa'): mode = key
            elif key == 'variante':
                mode = 'variante'; vlabel = val.split('|')[0].strip().rstrip('.')
                add_ed('variante_cabecalho', val, vlabel)
            elif key == 'texto': L['texto_titulo'] = val; mode = 'inter'
            elif key == 'titulo_trad': L['trad_titulo'] = val
            elif key == 'secao':
                sec = val.split('|')[0].strip().rstrip('.'); add_ed('secao_texto_bororo', val, sec)
            elif key == 'secao_trad': add_ed('secao_traducao', val, val.strip().rstrip('.'))
            elif key == 's':
                sent = int(val); cell_i = 0; mode = 'inter'
                trans.setdefault(sent, {})['sec'] = sec
            elif key == 't':
                n, _, txt = val.partition(' ')
                trans.setdefault(int(n), {}).update(pt=txt, pt_page=page)
            elif key == 'n':
                n, _, txt = val.partition(' ')
                notes[int(n)] = dict(pagina=page, texto=txt)
            elif key == 'foto': add_ed('legenda_foto', val)
            elif key == 'ciclo': add_ed('ciclo', val)
            else:
                raise SystemExit(f'{path.name}:{n_line}: marcador desconhecido @{key}')
            continue
        if mode in ('intro', 'narrativa', 'variante'):
            add_ed(mode, line, vlabel if mode == 'variante' else '')
        elif '|' in line:
            if sent is None:
                raise SystemExit(f'{path.name}:{n_line}: célula antes da primeira frase')
            bo, _, gl = (p.strip() for p in line.partition('|'))
            m = NOTE.search(bo); nota = ''
            if m:
                nota = m.group(1); bo = (bo[:m.start()] + bo[m.end():]).strip()
            cell_i += 1
            cells.append(dict(sentenca=sent, celula=cell_i, pagina=page, bororo=bo,
                              bororo_norm=norm_text(bo), glosa=gl, nota=nota))
        else:
            raise SystemExit(f'{path.name}:{n_line}: linha fora de bloco: {line[:60]}')
    return L, ed, cells, trans, notes


def corbo_vocab() -> set[str]:
    """Formas já atestadas no CorBo (CoNLL-U + coleções documentais não bíblicas), para conferência."""
    v = set()
    conllu = ROOT / 'CorBo/Corpus_Files/CorBo.conllu'
    if conllu.exists():
        for line in conllu.open(encoding='utf-8'):
            p = line.split('\t')
            if len(p) == 10 and p[0].isdigit():
                v.add(p[1].lower())
    for f in glob.glob(str(ROOT / 'CorBo_vNext/texts/**/*.tsv'), recursive=True):
        if any(x in f for x in ('biblia', 'bakaru-maiwu', 'pao-kurirewu', 'enciclopedia-bororo-ii')):
            continue
        v.update(w.lower() for w in re.findall(r'[A-Za-z]+', Path(f).read_text(encoding='utf-8', errors='ignore')))
    return v


def build(write=True):
    U, I, N, E = [], [], [], []
    problems = 0
    for f in sorted(SRC.glob('lenda*.txt')):
        L, ed, cells, trans, notes = parse(f)
        ln = L['lenda']; pre = f'{PREFIX}-{ln:02d}'
        for e in ed:
            e['id'] = f"{pre}-ED{e['ordem']:03d}"; e['titulo'] = L['titulo']; E.append(e)
        sents = sorted({c['sentenca'] for c in cells})
        for i, c in enumerate(cells):
            prev = cells[i - 1] if i else None
            c['ligada'] = ''
            if is_bound(c['bororo_norm']):
                if prev and prev['sentenca'] == c['sentenca'] and prev['bororo_norm'][-1:].isalpha():
                    c['ligada'] = '1'
                else:
                    print(f"  ATENÇÃO {c['bororo']} não ligado (início de frase ou depois de pontuação): {pre}-{c['sentenca']:03d}")
                    problems += 1
        for s in sents:
            cs = [c for c in cells if c['sentenca'] == s]
            uid = f'{pre}-{s:03d}'
            for c in cs:
                c['unit_id'] = uid; I.append(c)
            src = ' '.join(c['bororo'] for c in cs)
            t = trans.get(s, {})
            p0, p1 = cs[0]['pagina'], cs[-1]['pagina']
            U.append(dict(id=uid, lenda=ln, titulo=L['titulo'], texto_bororo_titulo=L['texto_titulo'],
                          titulo_traducao=L['trad_titulo'], secao=t.get('sec', 'Texto principal'), numero=s,
                          pagina=p0 if p0 == p1 else f'{p0}-{p1}', source=src, bororo=join_cells(cs),
                          portuguese=t.get('pt', ''), pagina_traducao=t.get('pt_page', ''),
                          notas=','.join(c['nota'] for c in cs if c['nota']), editorial_note=''))
        ref = {}
        for c in cells:
            if c['nota']:
                ref.setdefault(int(c['nota']), []).append(f"{pre}-{c['sentenca']:03d}")
        for n in sorted(notes):
            N.append(dict(id=f'{pre}-N{n:02d}', lenda=ln, nota=n, pagina=notes[n]['pagina'],
                          unidades=','.join(dict.fromkeys(ref.get(n, []))), texto=notes[n]['texto']))
        miss_t = [s for s in sents if not trans.get(s, {}).get('pt')]
        extra_t = [s for s in trans if trans[s].get('pt') and s not in sents]
        miss_n = sorted(set(ref) - set(notes)); unused = sorted(set(notes) - set(ref))
        gaps = [s for s in range(1, max(sents) + 1) if s not in sents]
        print(f'lenda {ln} ({L["titulo"]}): {len(sents)} frases, {len(cells)} células, {len(notes)} notas, {len(ed)} blocos editoriais')
        for label, val in (('frases sem tradução', miss_t), ('traduções sem frase', extra_t),
                           ('notas chamadas sem texto', miss_n), ('notas sem chamada', unused), ('lacunas na numeração', gaps)):
            if val:
                problems += 1; print(f'  ATENÇÃO {label}: {val}')
    vocab = corbo_vocab(); rep = {}
    toks = []                                  # (forma impressa, unidade), com nure/rogu ligados
    for c in I:
        ws = [w.rstrip("-'") for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", c['bororo'])]
        if c['ligada'] and toks and ws:
            toks[-1] = (toks[-1][0] + ' ' + ws[0], toks[-1][1]); ws = ws[1:]
        for w in ws:
            if toks and w.lower() in BOUND and toks[-1][1] == c['unit_id'] and len(ws) > 1:
                toks[-1] = (toks[-1][0] + ' ' + w, toks[-1][1])
            else:
                toks.append((w, c['unit_id']))
    for w0, uid in toks:
        if True:
            n = norm_text(w0).lower()
            r = rep.setdefault(n, dict(normalizada=n, originais=set(), ocorrencias=0, unidades=[], regra_wu=''))
            r['originais'].add(w0); r['ocorrencias'] += 1; r['unidades'].append(uid)
            if VOWEL_U.search(w0.replace('-', '').replace("'", '')):
                r['regra_wu'] = 'sim'
    for r in rep.values():
        r['atestada'] = 'sim' if r['normalizada'] in vocab else 'não'
        r['originais'] = ' '.join(sorted(r['originais'])); r['unidades'] = ','.join(dict.fromkeys(r['unidades']))
    R = sorted(rep.values(), key=lambda r: (r['atestada'], -r['ocorrencias'], r['normalizada']))
    print(f"formas: {len(R)}; não atestadas no CorBo: {sum(r['atestada'] == 'não' for r in R)}; "
          f"regra -wu: {[r['normalizada'] for r in R if r['regra_wu']]}")
    if not write:
        return problems

    def w(name, rows, cols):
        with open(COL / name, 'w', newline='', encoding='utf-8') as fh:
            wr = csv.DictWriter(fh, cols, delimiter='\t', extrasaction='ignore', lineterminator='\n')
            wr.writeheader(); wr.writerows(rows)
    w('enciclopedia_ii_parallel.tsv', U, ['id', 'lenda', 'titulo', 'texto_bororo_titulo', 'titulo_traducao', 'secao', 'numero',
                                         'pagina', 'source', 'bororo', 'portuguese', 'pagina_traducao', 'notas', 'editorial_note'])
    w('enciclopedia_ii_interlinear.tsv', I, ['unit_id', 'sentenca', 'celula', 'pagina', 'bororo', 'bororo_norm', 'ligada', 'glosa', 'nota'])
    w('enciclopedia_ii_notas.tsv', N, ['id', 'lenda', 'nota', 'pagina', 'unidades', 'texto'])
    w('enciclopedia_ii_editorial.tsv', E, ['id', 'lenda', 'titulo', 'ordem', 'tipo', 'rotulo', 'pagina', 'texto'])
    w('enciclopedia_ii_normalizacao.tsv', R, ['normalizada', 'originais', 'ocorrencias', 'atestada', 'regra_wu', 'unidades'])
    for ln in sorted({u['lenda'] for u in U}):
        with open(COL / f'enciclopedia_ii_lenda{ln:02d}_paralelo.txt', 'w', encoding='utf-8') as fh:
            sec = None
            for u in (x for x in U if x['lenda'] == ln):
                if u['secao'] != sec:
                    sec = u['secao']; fh.write(f'# {sec}\n\n')
                fh.write(f"{u['bororo']}\n{u['portuguese']}\n\n")
    print(f'gravado em {COL.relative_to(ROOT)}')
    return problems


if __name__ == '__main__':
    sys.exit(1 if build(write='--check' not in sys.argv) else 0)
