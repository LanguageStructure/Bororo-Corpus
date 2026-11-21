/* Visão geral da página de estatísticas: números e gráficos pré-calculados
   (data/statistics-summary.json, gerado por scripts/build_statistics_summary.py). */
(async () => {
  'use strict';
  const box = document.getElementById('statsOverview');
  if (!box) return;
  const fmt = n => Number(n || 0).toLocaleString('pt-BR');
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const UPOS = {NOUN:'substantivo',VERB:'verbo',ADV:'advérbio',ADP:'posposição',PRON:'pronome',PROPN:'nome próprio',DET:'determinante',
    X:'outra classe',PART:'partícula',AUX:'auxiliar',INTJ:'interjeição',CCONJ:'conj. coordenativa',SCONJ:'conj. subordinativa',NUM:'numeral',ADJ:'adjetivo'};
  let d;
  try { const r = await fetch('./data/statistics-summary.json', {cache: 'no-cache'}); if (!r.ok) throw Error(r.status); d = await r.json(); }
  catch (e) { box.innerHTML = '<p class="muted">Resumo indisponível.</p>'; return; }

  const c = d.conllu || {};
  const tiles = [
    ['unidades documentais', d.units], ['tokens nos textos', d.tokens], ['formas distintas', d.types],
    ['sentenças no CoNLL-U', c.sentences], ['sentenças gold', c.gold_sentences],
  ];
  // Barras horizontais de uma só série: rótulo à esquerda, valor à direita, dica ao passar o mouse.
  const bars = (rows, unit) => {
    const max = Math.max(...rows.map(r => r[1]), 1);
    return '<div class="ov-bars" role="list">' + rows.map(([label, v, extra]) =>
      `<div class="ov-row" role="listitem" title="${esc(label)}: ${fmt(v)} ${unit}${extra ? ' · ' + esc(extra) : ''}">` +
      `<span class="ov-label">${esc(label)}</span><span class="ov-track"><span class="ov-fill" style="width:${Math.max(0.5, 100 * v / max)}%"></span></span>` +
      `<span class="ov-val">${fmt(v)}</span></div>`).join('') + '</div>';
  };
  const table = (head, rows) => '<details class="ov-table"><summary>Ver como tabela</summary><table><thead><tr>' +
    head.map(h => `<th>${esc(h)}</th>`).join('') + '</tr></thead><tbody>' +
    rows.map(r => '<tr>' + r.map((x, i) => `<td${i ? ' class="n"' : ''}>${typeof x === 'number' ? fmt(x) : esc(x)}</td>`).join('') + '</tr>').join('') + '</tbody></table></details>';

  const top = d.collections.slice(0, 12);
  const rest = d.collections.slice(12);
  const collRows = top.map(([k, u, t]) => [k, t, `${fmt(u)} unidades`]);
  if (rest.length) collRows.push([`Outras (${rest.length})`, rest.reduce((n, x) => n + x[2], 0), `${fmt(rest.reduce((n, x) => n + x[1], 0))} unidades`]);
  const uposTotal = d.upos.reduce((n, x) => n + x[1], 0);

  // Composição por tipo de material (grupo do índice documental), com a fatia bíblica explícita.
  function groupCard() {
    if (!Array.isArray(d.groups) || !d.groups.length) return '';
    const BIB = ['Novo Testamento', 'Antigo Testamento', 'Textos bíblicos'];
    const total = d.groups.reduce((n, g) => n + g[2], 0) || 1;
    const bib = d.groups.filter(g => BIB.includes(g[0])).reduce((n, g) => n + g[2], 0);
    return `<section class="ov-card" style="margin-top:16px"><h2>Composição por tipo de material</h2>` +
      `<p class="muted">Textos bíblicos (traduções) somam ${(100 * bib / total).toFixed(1).replace('.', ',')}% dos tokens; ` +
      `considere isso ao comparar frequências ou treinar modelos.</p>` +
      bars(d.groups.map(([g, u, t]) => [g, t, `${fmt(u)} unidades · ${(100 * t / total).toFixed(1).replace('.', ',')}%`]), 'tokens') +
      table(['Tipo de material', 'Unidades', 'Tokens'], d.groups) + '</section>';
  }
  box.innerHTML =
    '<div class="ov-tiles">' + tiles.map(([l, v]) => `<div class="ov-tile"><div class="ov-num">${fmt(v)}</div><div class="ov-lab">${esc(l)}</div></div>`).join('') + '</div>' +
    '<div class="ov-grid">' +
      `<section class="ov-card"><h2>Tokens por coleção</h2><p class="muted">Índice documental publicado · ${fmt(d.tokens)} tokens</p>${bars(collRows, 'tokens')}` +
        table(['Coleção', 'Unidades', 'Tokens'], d.collections) + '</section>' +
      `<section class="ov-card"><h2>Classes gramaticais no CoNLL-U</h2><p class="muted">${fmt(uposTotal)} tokens anotados, sem pontuação · ${String(c.pct_tokens_automatic ?? '–').replace('.', ',')}% com algum campo automático</p>` +
        bars(d.upos.slice(0, 12).map(([u, n]) => [UPOS[u] || u, n, `${(100 * n / uposTotal).toFixed(1).replace('.', ',')}%`]), 'tokens') +
        table(['Classe (UPOS)', 'Tokens'], d.upos.map(([u, n]) => [`${UPOS[u] || u} (${u})`, n])) +
        '<p class="muted" style="margin-top:10px"><a href="coverage.html">Gold, silver e cobertura da anotação →</a></p></section>' +
    '</div>' + groupCard() + `<p class="muted ov-note">Resumo pré-calculado em ${esc(d.generated)}.</p>`;
})();
