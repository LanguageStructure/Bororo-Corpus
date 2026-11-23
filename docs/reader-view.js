/* Modos de leitura nos leitores de textos (injetado por site-header.js em páginas com .unit):
   - Cartões (padrão) ou Texto corrido (Bororo e português lado a lado, sem moldura);
   - Interlinear: forma, segmentação e glosa automática, para as unidades que têm
     sentença anotada no CoNLL-U (docs/data/interlinear.json);
   - pontuação colada à palavra na exibição (os dados não mudam);
   - selo "provisória" mostrado uma única vez quando vale para todas as unidades. */
(() => {
  'use strict';
  if (window.CorBoReaderView) return;
  window.CorBoReaderView = true;
  const en = document.documentElement.lang.startsWith('en');
  const T = en
    ? {cards: 'Cards', flow: 'Running text', igt: 'Interlinear', mode: 'Reading mode',
       allprov: 'All units shown are provisional (no editorial review yet).',
       note: 'Automatic gloss from the CoNLL-U annotation (lemma, features, Morph=) and the dictionary; not a reviewed gloss.',
       tree: 'tree'}
    : {cards: 'Cartões', flow: 'Texto corrido', igt: 'Interlinear', mode: 'Modo de leitura',
       allprov: 'Todas as unidades exibidas são provisórias (ainda sem revisão editorial).',
       note: 'Glosa gerada automaticamente da anotação do CoNLL-U (lema, traços, Morph=) e do dicionário; não substitui uma glosa revisada.',
       tree: 'árvore'};
  const BOR = '.bor, .bororo-text, .bororo, [lang="bor"]';
  const POR = '.por, .pt, .portuguese, .translation';
  const STATUS = '.status.provisional, .provisional';
  const store = {
    get(k, d) { try { return localStorage.getItem('cb-rv-' + k) ?? d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem('cb-rv-' + k, v); } catch { /* sem armazenamento */ } },
  };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  const css = document.createElement('style');
  css.textContent = `
  .cb-rv{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;margin:0 0 14px;font:14px system-ui,sans-serif;color:#3d4a45}
  .cb-rv .seg{display:inline-flex;border:1px solid #cfd8d3;border-radius:999px;overflow:hidden}
  .cb-rv .seg button{border:0;background:#fff;padding:5px 14px;font:inherit;color:inherit;cursor:pointer}
  .cb-rv .seg button[aria-pressed=true]{background:#2f4a40;color:#fff}
  .cb-rv label{display:inline-flex!important;gap:6px;align-items:center;cursor:pointer;width:auto!important;margin:0!important;flex:0 0 auto;font:inherit;color:inherit}
  .cb-rv label input{width:auto!important;margin:0!important}
  .cb-rv label[hidden]{display:none!important}
  .cb-rv .cb-rv-prov{font-size:13px;color:#66736e}
  .cb-rv .cb-rv-note{flex-basis:100%;font-size:12.5px;color:#66736e;margin:0}
  .cb-allprov ${STATUS.split(',').join(', .cb-allprov ')}{display:none}
  .cb-flow .unit{border:0!important;box-shadow:none!important;background:none!important;padding:3px 0!important;margin:0!important;border-radius:0!important;
    display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:32px;align-items:baseline}
  .cb-flow .unit > :not(${BOR.split(',').join('):not(')}):not(${POR.split(',').join('):not(')}):not(.cb-igt){display:none!important}
  .cb-flow .unit > :is(${BOR}){grid-column:1;margin:0!important;font-size:1.05em;line-height:1.6}
  .cb-flow .unit > :is(${POR}){grid-column:2;margin:0!important;color:#4b5853;line-height:1.55;border:0!important;padding:0!important}
  .cb-flow .unit > :is(${BOR}),.cb-flow .unit > :is(${POR}){grid-row:1}
  .cb-flow .unit > .cb-igt{grid-column:1 / -1;grid-row:2}
  .cb-flow .unit:not(:has(> :is(${POR}))){display:block}
  .cb-flow .unit:not(:has(> :is(${POR}))) > :is(${BOR}){display:inline}
  .cb-flow .unit.cb-target{outline:0;background:#f2f6f4!important}
  @media (max-width:700px){.cb-flow .unit{display:block}.cb-flow .unit > :is(${POR}){font-size:.92em;margin-bottom:10px!important}}
  .cb-igt{display:none;flex-wrap:wrap;gap:10px 16px;margin:10px 0 4px;padding:10px 12px;border-left:3px solid #c9d6d0;background:#f7faf8;border-radius:0 6px 6px 0}
  .cb-show-igt .cb-igt{display:flex}
  .cb-igt .w{display:inline-grid;grid-auto-rows:auto;row-gap:1px;line-height:1.35}
  .cb-igt .f{font-family:"Gentium Book Plus","Charis SIL",Georgia,serif;font-size:1.02em}
  .cb-igt .s{font-family:"Gentium Book Plus","Charis SIL",Georgia,serif;font-style:italic;color:#3d5a50;min-height:1.2em}
  .cb-igt .g{font:13px system-ui,sans-serif;color:#2f3a36;min-height:1.2em}
  .cb-igt.noseg .s{display:none}
  .cb-igt .sc{font-variant:small-caps;text-transform:lowercase;letter-spacing:.02em}
  .cb-igt a.tree{align-self:end;font:12px system-ui,sans-serif;color:#527066;margin-left:auto}`;
  document.head.append(css);

  /* pontuação colada na exibição */
  const PUNCT_BEFORE = /\s+(?=[.,;:!?…»)\]”’])/g;
  const PUNCT_AFTER = /([(\[«“‘])\s+/g;
  function tidy(el) {
    if (el.dataset.cbTidy) return;
    el.dataset.cbTidy = '1';
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (w.nextNode()) nodes.push(w.currentNode);
    for (const n of nodes) {
      const v = n.nodeValue.replace(PUNCT_BEFORE, '').replace(PUNCT_AFTER, '$1');
      if (v !== n.nodeValue) n.nodeValue = v;
    }
  }

  /* glosa interlinear */
  let IGT = null;
  let igtLoad = null;
  const loadIGT = () => igtLoad || (igtLoad = fetch('data/interlinear.json').then(r => r.ok ? r.json() : {units: {}})
    .then(d => { IGT = d.units || {}; return IGT; }).catch(() => { IGT = {}; return IGT; }));
  const sc = s => esc(s).replace(/\b([0-9]*[A-Z][A-Z0-9]*)\b/g, '<span class="sc">$1</span>');
  function igtHTML(rec) {
    const words = [];
    for (const [f, s, g] of rec.t) {
      if (!g && !s && words.length && /^[^\p{L}\p{N}]+$/u.test(f)) { words[words.length - 1].f += f; continue; }
      words.push({f, s, g});
    }
    const cells = words.map(w => `<span class="w"><span class="f">${esc(w.f)}</span><span class="s">${esc(w.s)}</span><span class="g">${sc(w.g)}</span></span>`).join('');
    const tree = rec.sid ? `<a class="tree" href="ud.html#${encodeURIComponent(rec.sid)}" title="sent_id ${esc(rec.sid)}">${T.tree} ↗</a>` : '';
    return cells + tree;
  }
  function addIGT(unit) {
    if (!IGT || unit.querySelector(':scope > .cb-igt')) return;
    const rec = IGT[unit.id];
    if (!rec) return;
    const box = document.createElement('div');
    box.className = 'cb-igt' + (rec.t.some(t => t[1]) ? '' : ' noseg');
    box.innerHTML = igtHTML(rec);
    const bor = unit.querySelector(BOR);
    (bor && bor.parentElement === unit ? bor : unit.lastElementChild).after(box);
  }

  /* barra de modos */
  let bar = null;
  let mode = store.get('mode', 'cards');
  let igtOn = store.get('igt', '0') === '1';
  function apply() {
    document.body.classList.toggle('cb-flow', mode === 'flow');
    document.body.classList.toggle('cb-show-igt', igtOn);
    if (!bar) return;
    bar.querySelectorAll('.seg button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.m === mode)));
    const cb = bar.querySelector('input');
    cb.checked = igtOn;
    bar.querySelector('.cb-rv-note').hidden = !igtOn;
  }
  function buildBar(first) {
    bar = document.createElement('div');
    bar.className = 'cb-rv';
    bar.setAttribute('role', 'toolbar');
    bar.setAttribute('aria-label', T.mode);
    bar.innerHTML = `<span class="seg"><button type="button" data-m="cards">${T.cards}</button><button type="button" data-m="flow">${T.flow}</button></span>` +
      `<label hidden><input type="checkbox"> ${T.igt}</label><span class="cb-rv-prov" hidden></span><p class="cb-rv-note" hidden>${T.note}</p>`;
    bar.querySelectorAll('.seg button').forEach(b => b.addEventListener('click', () => { mode = b.dataset.m; store.set('mode', mode); apply(); }));
    bar.querySelector('input').addEventListener('change', e => {
      igtOn = e.target.checked;
      store.set('igt', igtOn ? '1' : '0');
      if (igtOn) loadIGT().then(() => { document.querySelectorAll('.unit').forEach(addIGT); refreshIGTState(); });
      apply();
    });
    // a barra vai antes do bloco que contém todas as unidades (algumas páginas agrupam por seção)
    const units = [...document.querySelectorAll('.unit')];
    let anc = first.parentElement;
    while (anc.parentElement && !anc.contains(units[units.length - 1])) anc = anc.parentElement;
    let ref = first;
    while (ref.parentElement !== anc) ref = ref.parentElement;
    // sobe também por título e linha de autoria de seção logo antes da primeira unidade (ex.: Boe Ero)
    for (let k = 0; k < 3 && ref.previousElementSibling &&
         ref.previousElementSibling.matches('h2,h3,h4,.section,.meta,.text-meta,.byline,.sec-meta,small'); k++) {
      ref = ref.previousElementSibling;
    }
    anc.insertBefore(bar, ref);
    apply();
  }
  function refreshIGTState() {
    if (!bar || !IGT) return;
    const any = [...document.querySelectorAll('.unit')].some(u => IGT[u.id]);
    // sem nenhuma unidade anotada na página, a opção nem aparece
    bar.querySelector('label').hidden = !any;
    if (!any) document.body.classList.remove('cb-show-igt');
    else document.body.classList.toggle('cb-show-igt', igtOn);
    bar.querySelector('.cb-rv-note').hidden = !(any && igtOn);
  }

  function scan() {
    const units = [...document.querySelectorAll('.unit')];
    if (!units.length) return;
    if (!bar || !bar.isConnected) buildBar(units[0]);
    for (const u of units) {
      u.querySelectorAll(`:scope > :is(${BOR}), :scope > :is(${POR})`).forEach(tidy);
      if (IGT) addIGT(u);
    }
    const prov = units.filter(u => u.querySelector(STATUS)).length;
    const all = prov > 0 && prov === units.length;
    document.body.classList.toggle('cb-allprov', all);
    const p = bar.querySelector('.cb-rv-prov');
    p.hidden = !all;
    const txt = all ? T.allprov : '';
    if (p.textContent !== txt) p.textContent = txt;  // evita disparar o observador à toa
    refreshIGTState();
  }
  let pending = false;
  new MutationObserver(() => { if (!pending) { pending = true; requestAnimationFrame(() => { pending = false; scan(); }); } })
    .observe(document.documentElement, {childList: true, subtree: true});
  const start = () => { scan(); loadIGT().then(scan); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
