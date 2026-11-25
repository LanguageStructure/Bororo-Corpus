#!/usr/bin/env python3
"""Importa o Novo Testamento *Pao Kurirewu Bataru Kurirewu* (Wycliffe/SIL, 2019) para o CorBo.

Entrada: texto corrido (um parágrafo por linha; títulos de seção em linhas curtas; números de versículo
embutidos no texto; o primeiro número de cada capítulo é o número do capítulo, e o versículo 1 não é numerado).

Saída: um TSV por livro em CorBo_vNext/texts/pao-kurirewu-bataru/<pasta>/<pasta>.tsv, no mesmo formato
do Bakaru Maiwu (id, book, book_code, chapter, verse, source, reviewed, editorial_note), mais um relatório
de importação com as anomalias de numeração.

Uso: python scripts/import_pao_kurirewu_bataru.py [ARQUIVO.txt] [--apply]
(sem --apply só simula; o arquivo-fonte padrão fica em CorBo_vNext/texts/pao-kurirewu-bataru/source/)
"""
import argparse, csv, re, sys
from pathlib import Path

# (código, pasta, nome no CorBo, título na fonte, nº de capítulos, versículos por capítulo — versificação padrão)
VERSES = {
 'MAT': [25,23,17,25,48,34,29,34,38,42,30,50,58,36,39,28,27,35,30,34,46,46,39,51,46,75,66,20],
 'MRK': [45,28,35,41,43,56,37,38,50,52,33,44,37,72,47,20],
 'LUK': [80,52,38,44,39,49,50,56,62,42,54,59,35,35,32,31,37,43,48,47,38,71,56,53],
 'JHN': [51,25,36,54,47,71,53,59,41,42,57,50,38,31,27,33,26,40,42,31,25],
 'ACT': [26,47,26,37,42,15,60,40,43,48,30,25,52,28,41,40,34,28,41,38,40,30,35,27,27,32,44,31],
 'ROM': [32,29,31,25,21,23,25,39,33,21,36,21,14,23,33,27],
 '1CO': [31,16,23,21,13,20,40,13,27,33,34,31,13,40,58,24],
 '2CO': [24,17,18,18,21,18,16,24,15,18,33,21,14],
 'GAL': [24,21,29,31,26,18], 'EPH': [23,22,21,32,33,24], 'PHP': [30,30,21,23], 'COL': [29,23,25,18],
 '1TH': [10,20,13,18,28], '2TH': [12,17,18], '1TI': [20,15,16,16,25,21], '2TI': [18,26,17,22],
 'TIT': [16,15,15], 'PHM': [25], 'HEB': [14,18,19,16,14,20,28,13,28,39,40,29,25],
 'JAS': [27,26,18,17,20], '1PE': [25,25,22,19,14], '2PE': [21,22,18], '1JN': [10,29,24,21,21],
 '2JN': [13], '3JN': [15], 'JUD': [25], 'REV': [20,29,22,11,14,17,17,13,21,11,19,18,18,20,8,21,18,24,21,15,27,21],
}
BOOKS = [  # código, pasta (igual à do Bakaru Maiwu), nome, linha de título na fonte
 ('MAT','mateus','MATEUS','Mateus'), ('MRK','marcos','MARCOS','Marcos'), ('LUK','lucas','LUCAS','Lucas'),
 ('JHN','joao','JOÃO','João'), ('ACT','atos','ATOS','Atos'), ('ROM','romanos','ROMANOS','Romanos'),
 ('1CO','1-corintios','1 CORÍNTIOS','1 Coríntios'), ('2CO','2-corintios','2 CORÍNTIOS','2 Coríntios'),
 ('GAL','galatas','GÁLATAS','Gálatas'), ('EPH','efesios','EFÉSIOS','Efésios'), ('PHP','filipenses','FILIPENSES','Filipenses'),
 ('COL','colossenses','COLOSSENSES','Colossenses'), ('1TH','1-tessalonicenses','1 TESSALONICENSES','1 Tessalonicenses'),
 ('2TH','2-tessalonicenses','2 TESSALONICENSES','2 Tessalonicenses'), ('1TI','1-timoteo','1 TIMÓTEO','1 Timóteo'),
 ('2TI','2-timoteo','2 TIMÓTEO','2 Timóteo'), ('TIT','tito','TITO','Tito'), ('PHM','filemon','FILEMOM','Filemom'),
 ('HEB','hebreus','HEBREUS','Hebrewus'), ('JAS','tiago','TIAGO','Tiago'), ('1PE','1-pedro','1 PEDRO','1 Pedro'),
 ('2PE','2-pedro','2 PEDRO','2 Pedro'), ('1JN','1-joao','1 JOÃO','1 João'), ('2JN','2-joao','2 JOÃO','2 João'),
 ('3JN','3-joao','3 JOÃO','3 João'), ('JUD','judas','JUDAS','Judas'), ('REV','apocalipse','APOCALIPSE',None),
]
PREFIX = 'BOR-CORBO-PKB'
NUM = re.compile(r'(?<!\S)(\d{1,3})(?:\s*[–-]\s*(\d{1,3}))?(?=\s)')


def vid(v1, v2=None):
    return f'{v1:03d}' + (f'_{v2:03d}' if v2 else '')


def parse(lines):
    title_to_idx = {b[3]: i for i, b in enumerate(BOOKS) if b[3]}
    start = next(i for i, l in enumerate(lines) if l.strip() == 'Mateus')
    header = [l.strip() for l in lines[:start] if l.strip()]
    rows, report = [], []
    bi, ch, v, cur = -1, 0, 0, None   # cur = linha (dict) do versículo em curso
    heading = []

    def flush_heading(lineno):
        nonlocal heading
        if heading and bi >= 0:
            code = BOOKS[bi][0]
            hid = f'{PREFIX}-{code}-{max(ch,1):03d}-HEAD-{sum(1 for r in rows if r["book_code"]==code and "-HEAD-" in r["id"])+1:03d}'
            rows.append(dict(id=hid, book=BOOKS[bi][2], book_code=code, chapter=str(max(ch, 1)), verse='',
                             source=' '.join(heading), reviewed='', editorial_note='Título de seção da fonte.',
                             _line=lineno, _after=f'{ch}:{v}'))
        heading = []

    def new_verse(c, a, b, lineno):
        nonlocal cur
        code = BOOKS[bi][0]
        cur = dict(id=f'{PREFIX}-{code}-{c:03d}-{vid(a, b)}', book=BOOKS[bi][2], book_code=code, chapter=str(c),
                   verse=f'{a}-{b}' if b else str(a), source='', reviewed='', editorial_note='', _line=lineno)
        rows.append(cur)

    for n, raw in enumerate(lines[start:], start + 1):
        s = raw.strip()
        if not s:
            continue
        if s in title_to_idx:                       # linha de título de livro
            flush_heading(n); heading = []
            bi, ch, v, cur = title_to_idx[s], 0, 0, None
            continue
        if not re.search(r'\d', s) and len(s) < 120:  # título de seção (pode ocupar várias linhas)
            heading.append(s)
            continue
        # parágrafo
        if bi >= 0 and BOOKS[bi][0] == 'JUD' and ch == 1 and v >= 24 and re.match(r'1\s', s):
            bi, ch, v, cur = title_to_idx['Judas'] + 1, 0, 0, None   # Apocalipse: sem linha de título na fonte
            report.append(dict(line=n, book='REV', ref='', kind='livro_sem_titulo',
                               detail='Apocalipse começa sem linha com o nome do livro; títulos antes: ' + ' / '.join(heading)))
        code = BOOKS[bi][0]
        vv = VERSES[code]
        markers = list(NUM.finditer(s))
        segs = []   # (início do texto, fim do marcador anterior)
        last_end = 0
        started = False
        for m in markers:
            a, b = int(m.group(1)), (int(m.group(2)) if m.group(2) else None)
            at_start = s[:m.start()].strip() == ''
            maxv = vv[ch - 1] if 1 <= ch <= len(vv) else 0
            kind = None
            nxt = next((int(x.group(1)) for x in markers if x.start() > m.end()), None)
            as_verse = v < a <= maxv + 1 and (b is None or b > a) and (
                a <= v + 4 or nxt == (b or a) + 1 or a >= maxv - 1)
            if ch == 0 and a == 1:
                kind = 'chapter'
            elif a == v + 1 and a <= maxv and b is None:
                kind = 'verse'           # ambíguo (v+1 == cap+1): versículo, porque o capítulo não terminou
            elif a == ch + 1 and ch < len(vv) and b is None and (v >= maxv - 3 or at_start):
                kind = 'chapter'
            elif as_verse:
                kind = 'verse'
            if kind is None:
                if a != v and not (b is None and a > 200):
                    report.append(dict(line=n, book=code, ref=f'{ch}:{v}', kind='numero_nao_usado',
                                       detail=s[max(0, m.start()-40):m.end()+40]))
                continue
            # texto entre o marcador anterior e este pertence ao versículo em curso
            chunk = s[last_end:m.start()].strip()
            if chunk:
                if cur is None:
                    report.append(dict(line=n, book=code, ref=f'{ch}:{v}', kind='texto_sem_versiculo', detail=chunk[:120]))
                else:
                    if heading and not started:
                        report.append(dict(line=n, book=code, ref=f'{ch}:{v}', kind='titulo_no_meio_do_versiculo',
                                           detail=' '.join(heading)))
                    cur['source'] += ' ' + chunk
            started = True
            flush_heading(n)
            if kind == 'chapter':
                if ch and v < vv[ch - 1]:
                    report.append(dict(line=n, book=code, ref=f'{ch}:{v}', kind='capitulo_incompleto',
                                       detail=f'cap. {ch} termina no v. {v} (esperado {vv[ch-1]})'))
                ch, v = a, 1
                new_verse(ch, 1, None, n)
            else:
                if a > v + 1 and v == 1 and cur is not None and cur['verse'] == '1':
                    # o primeiro bloco do capítulo (sem número) cobre os versículos 1..a-1
                    cur['verse'] = f'1-{a-1}'
                    cur['id'] = cur['id'][:-3] + vid(1, a - 1)
                    cur['editorial_note'] = f'A fonte agrupa os versículos 1–{a-1} sem numeração; faixa inferida na importação.'
                    report.append(dict(line=n, book=code, ref=f'{ch}:1-{a-1}', kind='faixa_inicial_inferida',
                                       detail=f'o texto antes do v. {a} foi tratado como {ch}:1–{a-1}'))
                elif a > v + 1:
                    report.append(dict(line=n, book=code, ref=f'{ch}:{a}', kind='versiculos_ausentes',
                                       detail=f'{ch}:{v+1}' + (f'–{a-1}' if a - 1 > v + 1 else '')))
                v = b or a
                new_verse(ch, a, b, n)
            last_end = m.end()
        chunk = s[last_end:].strip()
        if chunk:
            if cur is None:
                report.append(dict(line=n, book=code, ref=f'{ch}:{v}', kind='texto_sem_versiculo', detail=chunk[:120]))
            else:
                if heading and not started:
                    report.append(dict(line=n, book=code, ref=f'{ch}:{v}', kind='titulo_no_meio_do_versiculo',
                                       detail=' '.join(heading)))
                cur['source'] += ' ' + chunk
        if heading:
            flush_heading(n)
    for r in rows:
        r['source'] = re.sub(r'\s+', ' ', r['source']).strip()
        if not r['source']:
            report.append(dict(line=r['_line'], book=r['book_code'], ref=f"{r['chapter']}:{r['verse']}",
                               kind='versiculo_vazio', detail=r['id']))
    # capítulos faltando / último capítulo incompleto
    for code, *_ in BOOKS:
        got = {}
        for r in rows:
            if r['book_code'] == code and r['verse']:
                got.setdefault(int(r['chapter']), []).append(r)
        for c in range(1, len(VERSES[code]) + 1):
            if c not in got:
                report.append(dict(line='', book=code, ref=f'{c}', kind='capitulo_ausente', detail=''))
        if got:
            c = max(got)
            last = max(int(x['verse'].split('-')[-1]) for x in got[c])
            if last < VERSES[code][c - 1]:
                report.append(dict(line='', book=code, ref=f'{c}:{last}', kind='capitulo_incompleto',
                                   detail=f'cap. {c} termina no v. {last} (esperado {VERSES[code][c-1]})'))
    ids = [r['id'] for r in rows]
    dup = {i for i in ids if ids.count(i) > 1}
    for i in sorted(dup):
        report.append(dict(line='', book=i.split('-')[3], ref='', kind='id_duplicado', detail=i))
    return header, rows, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?', default='CorBo_vNext/texts/pao-kurirewu-bataru/source/NT_SIL.txt')
    ap.add_argument('--out', default='CorBo_vNext/texts/pao-kurirewu-bataru')
    ap.add_argument('--report', default='CorBo/validation/pao_kurirewu_bataru_import.tsv')
    ap.add_argument('--apply', action='store_true', help='grava os TSV (sem isto, só simula)')
    a = ap.parse_args()
    lines = Path(a.src).read_text(encoding='utf-8').split('\n')
    header, rows, report = parse(lines)
    cols = ['id', 'book', 'book_code', 'chapter', 'verse', 'source', 'reviewed', 'editorial_note']
    verses = [r for r in rows if r['verse']]
    print('Cabeçalho da fonte:', *header, sep='\n  ')
    print(f'{len(verses)} unidades de versículo, {len(rows)-len(verses)} títulos de seção, {len(report)} ocorrências no relatório')
    from collections import Counter
    print(Counter(x['kind'] for x in report))
    if not a.apply:
        print('Simulação: nada foi gravado (use --apply).')
        return
    out = Path(a.out)
    for code, folder, name, _ in BOOKS:
        br = [r for r in rows if r['book_code'] == code]
        if not br:
            continue
        p = out / folder / f'{folder}.tsv'
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('w', encoding='utf-8', newline='') as fh:
            w = csv.DictWriter(fh, cols, delimiter='\t', lineterminator='\n', extrasaction='ignore')
            w.writeheader(); w.writerows(br)
    rp = Path(a.report); rp.parent.mkdir(parents=True, exist_ok=True)
    with rp.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, ['line', 'book', 'ref', 'kind', 'detail', 'decisao'], delimiter='\t', lineterminator='\n',
                           extrasaction='ignore')
        w.writeheader(); w.writerows(report)
    print('Gravado em', out, 'e', rp)


if __name__ == '__main__':
    main()
