/* Painel lexical do CorBo: único para todos os leitores.
   Abre ao clicar em qualquer elemento .word; lê o índice pré-calculado em
   data/lexicon/<letra>.json (gerado por scripts/build_lexicon_panel.py).
   ← / → percorrem as palavras do texto; Esc fecha. */
(() => {
  'use strict';
  if (window.CorBoLexPanel) return;

  const css = `
  #corboLexPanel{position:fixed;z-index:2200;right:16px;top:16px;bottom:16px;width:400px;max-width:calc(100vw - 32px);
    display:flex;flex-direction:column;background:#fff;color:#202624;border:1px solid #dbe3de;border-radius:14px;
    box-shadow:0 16px 40px rgba(0,0,0,.14);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;box-sizing:border-box}
  #corboLexPanel[hidden]{display:none}
  #corboLexPanel *{box-sizing:border-box}
  #corboLexPanel .lp-head{padding:18px 20px 12px;border-bottom:1px solid #e8ece9;position:relative}
  #corboLexPanel .lp-form{font:600 28px/1.15 "Charis SIL","Gentium Book Plus",Georgia,serif;margin:0 64px 4px 0;overflow-wrap:anywhere}
  #corboLexPanel .lp-sub{color:#6d7672;font-size:13px}
  #corboLexPanel .lp-btns{position:absolute;right:12px;top:12px;display:flex;gap:2px}
  #corboLexPanel .lp-btns button{border:0;background:transparent;font-size:18px;width:32px;height:32px;border-radius:8px;cursor:pointer;color:#4b5450}
  #corboLexPanel .lp-btns button:hover{background:#eef3f1}
  #corboLexPanel .lp-body{overflow:auto;padding:6px 20px 20px;flex:1}
  #corboLexPanel h4{font:600 12px/1 system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#527066;margin:20px 0 9px}
  #corboLexPanel .lp-chips{display:flex;flex-wrap:wrap;gap:6px}
  #corboLexPanel .chip{background:#eef3f1;border-radius:999px;padding:3px 10px;font-size:13px}
  #corboLexPanel .chip b{font-weight:600}
  #corboLexPanel .morph{display:flex;flex-wrap:wrap;gap:4px;align-items:center;font:17px "Charis SIL","Gentium Book Plus",Georgia,serif}
  #corboLexPanel .morph span{border:1px solid #c9d6cf;border-radius:6px;padding:1px 8px;background:#fbfcfb}
  #corboLexPanel .morph i{color:#8a928e;font-style:normal}
  #corboLexPanel .st{display:inline-block;font-size:12px;border-radius:5px;padding:1px 7px;margin-left:6px}
  #corboLexPanel .st.confirmed{background:#e3f1e8;color:#25613d}#corboLexPanel .st.proposed{background:#fff3d9;color:#7a5600}
  #corboLexPanel .st.low{background:#fde8e4;color:#8a3324}#corboLexPanel .st.unanalysed{background:#eef0ef;color:#5f6763}
  #corboLexPanel .muted{color:#6d7672;font-size:13px}
  #corboLexPanel .dict{border-left:3px solid #527066;padding:2px 0 2px 10px;margin:8px 0}
  #corboLexPanel .dict .ipa{color:#6d7672;font-size:13px;margin-left:6px}
  #corboLexPanel .dict .pos{font-size:11px;color:#527066;border:1px solid #c9d6cf;border-radius:4px;padding:0 5px;margin-left:6px}
  #corboLexPanel .ex{background:#f7f9f8;border-radius:9px;padding:9px 11px;margin:8px 0}
  #corboLexPanel .ex .b{font:16px/1.5 "Charis SIL","Gentium Book Plus",Georgia,serif}
  #corboLexPanel .ex mark{background:#dcebe3;border-radius:3px;padding:0 2px}
  #corboLexPanel .ex .p{color:#4b5450;font-size:14px;margin-top:3px}
  #corboLexPanel .ex .src{color:#8a928e;font-size:11px;margin-top:4px}
  #corboLexPanel .bars div{display:grid;grid-template-columns:1fr 46px;gap:8px;align-items:center;font-size:13px;margin:4px 0}
  #corboLexPanel .bars .t{height:7px;background:#eef3f1;border-radius:4px;overflow:hidden;margin-top:3px}
  #corboLexPanel .bars .f{height:100%;background:#527066}
  #corboLexPanel .links{display:flex;flex-direction:column;gap:6px;margin-top:6px}
  #corboLexPanel .links a{color:#527066;text-decoration:none}#corboLexPanel .links a:hover{text-decoration:underline}
  .word.corbo-lex-active{background:#dcebe3;border-radius:3px;outline:1px solid #9fbfb0}
  @media(min-width:1100px){body.corbo-lex-open{padding-right:432px}}
  @media(max-width:760px){#corboLexPanel{top:auto;left:0;right:0;bottom:0;width:100%;max-width:none;max-height:72vh;border-radius:14px 14px 0 0}}`;
  const style = document.createElement('style');
  style.textContent = css;
  document.head.append(style);

  const panel = document.createElement('aside');
  panel.id = 'corboLexPanel';
  panel.className = 'corbo-lex-pop'; // compatibilidade com biblical-panel.js
  panel.hidden = true;
  panel.setAttribute('aria-label', 'Informações lexicais');
  panel.innerHTML = '<div class="lp-head"><div class="lp-form">Palavra</div><div class="lp-sub">Clique numa palavra do texto.</div>' +
    '<div class="lp-btns"><button type="button" data-k="prev" title="Palavra anterior (←)" aria-label="Palavra anterior">‹</button>' +
    '<button type="button" data-k="next" title="Próxima palavra (→)" aria-label="Próxima palavra">›</button>' +
    '<button type="button" data-k="close" title="Fechar (Esc)" aria-label="Fechar painel">×</button></div></div>' +
    '<div class="lp-body" aria-live="polite"></div>';
  document.body.append(panel);
  // Se outro script tornar o painel visível (ex.: leitores bíblicos), reserva o espaço.
  // Só empurra o conteúdo quando ele ocuparia o espaço do painel (algumas páginas já reservam a coluna direita).
  const needsRoom = () => {
    if (innerWidth < 1100) return false;
    document.body.classList.remove('corbo-lex-open');
    const c = document.querySelector('main, .wrap, .layout');
    return !c || c.getBoundingClientRect().right > innerWidth - 440;
  };
  const reserve = on => document.body.classList.toggle('corbo-lex-open', on && needsRoom());
  new MutationObserver(() => reserve(!panel.hidden))
    .observe(panel, {attributes: true, attributeFilter: ['hidden']});
  const head = panel.querySelector('.lp-head'), body = panel.querySelector('.lp-body');

  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const norm = s => String(s ?? '').normalize('NFC').toLocaleLowerCase('pt-BR').replace(/^[^\p{L}]+|[^\p{L}]+$/gu, '');
  const fmt = n => Number(n || 0).toLocaleString('pt-BR');
  const shardOf = f => { const c = f.normalize('NFD')[0] || ''; return c >= 'a' && c <= 'z' ? c : '_'; };

  const UPOS = {ADJ:'adjetivo',ADP:'posposição',ADV:'advérbio',AUX:'auxiliar',CCONJ:'conjunção coordenativa',DET:'determinante',
    INTJ:'interjeição',NOUN:'substantivo',NUM:'numeral',PART:'partícula',PRON:'pronome',PROPN:'nome próprio',PUNCT:'pontuação',
    SCONJ:'conjunção subordinativa',SYM:'símbolo',VERB:'verbo',X:'outra classe'};
  const FEAT = {
    Person:{1:'1ª pessoa',2:'2ª pessoa',3:'3ª pessoa'}, Number:{Sing:'singular',Plur:'plural',Sgtv:'singulativo',Col:'coletivo'},
    Clusivity:{In:'inclusivo',Ex:'exclusivo'}, Mood:{Ind:'indicativo',Sub:'subjuntivo',Imp:'imperativo',Quot:'quotativo',Opt:'optativo'},
    Status:{Irr:'irrealis'}, Nomzr:{Rel:'nominalização relativa',Loc:'nominalização locativa'}, Reflex:{Yes:'reflexivo'},
    Deixis:{Prox:'proximal',Med:'medial',Dist:'distal',Remt:'remoto'}, Polarity:{Neg:'negativo'},
    Voice:{Cau:'causativo',Pass:'passivo',CauPass:'causativo-passivo',CauInc:'causativo-incoativo'},
    Aspect:{Prog:'progressivo',Inc:'incoativo',IncProg:'incoativo-progressivo'}, Degree:{Dim:'diminutivo',Aug:'aumentativo'},
    Speech:{Quo:'discurso citado',Ind:'discurso indireto'}, Definite:{Ind:'indefinido'}, VerbForm:{Ger:'gerúndio'},
    PronType:{Art:'artigo',Prs:'pessoal',Int:'interrogativo',Dem:'demonstrativo',Rcp:'recíproco',Tot:'total',Ind:'indefinido'},
    Emph:{Yes:'enfático'}
  };
  const feats = s => !s || s === '_' ? [] : s.split('|').map(kv => {
    const [k, v] = kv.split('='); const base = k.replace(/\[psor\]$/, ''), ps = k !== base;
    const t = (FEAT[base] || {})[v] || (window.CorBoUDpt?.features?.[base]?.[v]) || `${base}=${v}`;
    return ps ? t + ' (possuidor)' : t;
  });
  const ST = {confirmed:['confirmed','segmentação confirmada'],proposed:['proposed','segmentação proposta'],
    proposed_low_support:['low','proposta com pouco suporte'],unanalysed:['unanalysed','sem segmentação'],hyp:['proposed','hipótese automática']};

  const cache = {};
  const loadShard = k => cache[k] ??= fetch(`./data/lexicon/${k}.json`).then(r => r.ok ? r.json() : {}).catch(() => ({}));

  let current = null, seq = 0;
  const words = () => [...document.querySelectorAll('.word')].filter(w => w.offsetParent !== null);

  function morphHTML(seg) {
    const parts = seg.split(/([-=])/);
    return '<div class="morph">' + parts.map(p => p === '-' ? '<i>-</i>' : p === '=' ? '<i>=</i>' : `<span>${esc(p === '0' ? 'Ø' : p)}</span>`).join('') + '</div>';
  }
  function snippet(text, form) {
    const re = new RegExp(`(^|[^\\p{L}])(${form.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})(?=[^\\p{L}]|$)`, 'iu');
    const m = re.exec(text); if (!m) return esc(text.slice(0, 160)) + (text.length > 160 ? '…' : '');
    const at = m.index + m[1].length, a = Math.max(0, at - 70), b = Math.min(text.length, at + form.length + 90);
    return (a ? '…' : '') + esc(text.slice(a, at)) + '<mark>' + esc(text.slice(at, at + form.length)) + '</mark>' + esc(text.slice(at + form.length, b)) + (b < text.length ? '…' : '');
  }

  function render(word, rec) {
    const ud = rec?.ud, tok = rec?.tok;
    const lemma = ud?.lemma?.[0]?.[0];
    head.querySelector('.lp-form').textContent = word;
    head.querySelector('.lp-sub').innerHTML = rec?.freq ? `${fmt(rec.freq)} ocorrência(s) nos textos` + (ud ? ` · ${fmt(ud.n)} no CoNLL-U` : '')
      : ud ? `${fmt(ud.n)} ocorrência(s) no CoNLL-U` : 'Forma não encontrada nos índices';
    let h = '';
    if (ud) {
      h += '<h4>Análise</h4><div class="lp-chips">';
      for (const [u] of ud.upos) h += `<span class="chip"><b>${esc(UPOS[u] || u)}</b></span>`;
      if (lemma) h += `<span class="chip">lema <b>${esc(lemma)}</b></span>`;
      h += '</div>';
      const ft = ud.feats.filter(([f]) => f && f !== '_');
      if (ft.length) h += '<div class="lp-chips" style="margin-top:8px">' + feats(ft[0][0]).map(t => `<span class="chip">${esc(t)}</span>`).join('') + '</div>' +
        (ft.length > 1 ? `<div class="muted" style="margin-top:4px">Outras análises: ${ft.slice(1).map(([f, n]) => esc(feats(f).join(', ')) + ` (${n})`).join('; ')}</div>` : '');
    }
    if (ud?.morph?.length || tok?.seg) {
      h += '<h4>Segmentação</h4>';
      if (ud?.morph?.length) h += morphHTML(ud.morph[0][0]) + '<div class="muted">anotada no CoNLL-U' + (ud.morph.length > 1 ? ' · variantes: ' + ud.morph.slice(1).map(([m]) => esc(m)).join(', ') : '') + '</div>';
      else if (tok?.seg) {
        const [cls, label] = ST[tok.st === 'unanalysed' ? 'hyp' : tok.st] || ST.hyp;
        h += morphHTML(tok.seg.join('-')) + `<div class="muted">tokenizador<span class="st ${cls}">${label}</span>` + (tok.support ? ` · ${tok.support} ocorrência(s) da família` : '') + (tok.concat === false ? ' · representação subjacente' : '') + '</div>';
      }
    }
    if (tok?.pt) h += `<p class="muted">Possível palavra portuguesa ou empréstimo (${esc(tok.pt)}).</p>`;
    if (ud?.gloss?.length) h += '<h4>Glosa</h4>' + ud.gloss.map(([g]) => esc(g)).join(' · ');
    if (rec?.dict?.length) {
      h += '<h4>Dicionário</h4>';
      for (const d of rec.dict) h += `<div class="dict"><b>${esc(d.entry)}</b>${d.ipa ? `<span class="ipa">[${esc(d.ipa)}]</span>` : ''}${d.pos ? `<span class="pos">${esc(d.pos)}</span>` : ''}` +
        `<div>${esc(d.definition || '')}</div>${d.example_sent ? `<div class="muted">${esc(d.example_sent)}</div>` : ''}</div>`;
    }
    if (rec?.ex?.length) {
      h += '<h4>No corpus</h4>';
      for (const e of rec.ex) h += `<div class="ex"><div class="b">${snippet(e.b, word)}</div><div class="p">${esc(e.p.slice(0, 200))}${e.p.length > 200 ? '…' : ''}</div><div class="src">${esc(e.c)} · ${esc(e.id)}</div></div>`;
    }
    if (rec?.coll?.length > 1) {
      const max = rec.coll[0][1];
      h += '<h4>Distribuição por coleção</h4><div class="bars">' + rec.coll.map(([c, n]) => `<div><div>${esc(c)}<div class="t"><div class="f" style="width:${100 * n / max}%"></div></div></div><span class="muted">${fmt(n)}</span></div>`).join('') + '</div>';
    }
    h += '<h4>Consultar</h4><div class="links">' +
      `<a href="word.html?form=${encodeURIComponent(word)}">Todas as ocorrências e concordância →</a>` +
      (ud?.sid ? `<a href="ud.html?sent_id=${encodeURIComponent(ud.sid)}">Árvore sintática de um exemplo →</a>` : '') +
      `<a href="dicionario.html?lemma=${encodeURIComponent(lemma || word)}">Dicionário →</a></div>`;
    if (!rec) h = '<p class="muted">Sem informação lexical registrada para esta forma.</p>' + h;
    body.innerHTML = h;
    body.scrollTop = 0;
  }

  async function open(el) {
    const word = norm(el.textContent);
    if (!word) return;
    document.querySelectorAll('.corbo-lex-active').forEach(x => x.classList.remove('corbo-lex-active'));
    el.classList.add('corbo-lex-active');
    current = el;
    const my = ++seq;
    panel.hidden = false;
    reserve(true);
    head.querySelector('.lp-form').textContent = word;
    head.querySelector('.lp-sub').textContent = 'Consultando…';
    const data = await loadShard(shardOf(word));
    if (my === seq) render(word, data[word]);
  }
  function close() {
    panel.hidden = true;
    document.body.classList.remove('corbo-lex-open');
    document.querySelectorAll('.corbo-lex-active').forEach(x => x.classList.remove('corbo-lex-active'));
  }
  function step(d) {
    const all = words(); if (!current) return;
    const i = all.indexOf(current); const next = all[i + d];
    if (next) { open(next); next.scrollIntoView({block: 'nearest', behavior: 'smooth'}); }
  }

  panel.addEventListener('click', e => {
    const k = e.target.closest('button')?.dataset.k;
    if (k === 'close') close(); else if (k === 'prev') step(-1); else if (k === 'next') step(1);
  });
  document.addEventListener('click', e => {
    const w = e.target.closest('.word');
    if (!w || panel.contains(w)) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    open(w);
  }, true);
  document.addEventListener('keydown', e => {
    if (panel.hidden || /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName)) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
  });
  window.CorBoLexPanel = {open, close};
})();
