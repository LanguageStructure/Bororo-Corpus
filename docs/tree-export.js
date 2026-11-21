/* Visualizador CoNLL-U: botão "Baixar SVG" em cada árvore. Gera um SVG autônomo
   (arcos, relações e palavras com lema e classe), pronto para artigos e slides. */
(() => {
  'use strict';
  const ACCENT = '#527066', INK = '#202624', MUTED = '#6d7672', W = 130;
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const style = document.createElement('style');
  style.textContent = '.cb-tree-dl{margin:6px 0 0;border:1px solid #c9d6cf;background:#fff;color:#527066;border-radius:6px;padding:4px 10px;font:13px system-ui;cursor:pointer}';
  document.head.append(style);

  function toSVG(tree) {
    const arcs = tree.querySelector('svg.arcs');
    const toks = [...tree.querySelectorAll('.tokens > .tok')];
    if (!arcs || !toks.length) return null;
    const width = Number(arcs.getAttribute('width')), h = Number(arcs.getAttribute('height'));
    const inner = arcs.innerHTML.replaceAll('var(--accent)', ACCENT);
    const words = toks.map((t, i) => {
      const x = (i + 0.5) * W, sm = t.querySelectorAll('small');
      const root = t.classList.contains('root');
      return `<text x="${x}" y="${h + 22}" text-anchor="middle" font-family="Gentium Book Plus, Charis SIL, Georgia, serif" font-size="17" font-weight="${root ? 700 : 400}" fill="${INK}">${esc(t.querySelector('b')?.textContent)}</text>` +
        `<text x="${x}" y="${h + 40}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" fill="${MUTED}">${esc(sm[0]?.textContent)}</text>` +
        `<text x="${x}" y="${h + 55}" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" fill="${ACCENT}">${esc(sm[1]?.textContent)}</text>`;
    }).join('');
    return `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${h + 66}" viewBox="0 0 ${width} ${h + 66}">` +
      `<rect width="100%" height="100%" fill="#fff"/>${inner}${words}</svg>\n`;
  }
  function add(tree) {
    if (tree.dataset.cbDl) return;
    tree.dataset.cbDl = '1';
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'cb-tree-dl';
    b.textContent = document.documentElement.lang.startsWith('en') ? 'Download SVG' : 'Baixar SVG';
    b.addEventListener('click', () => {
      const svg = toSVG(tree);
      if (!svg) return;
      const card = tree.closest('[id], article, section, .card');
      const name = (card?.id || 'arvore').replace(/[^\w.-]+/g, '_');
      const a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([svg], {type: 'image/svg+xml'}));
      a.download = `corbo-${name}.svg`;
      document.body.append(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    });
    tree.after(b);
  }
  const scan = () => document.querySelectorAll('.tree').forEach(add);
  new MutationObserver(scan).observe(document.documentElement, {childList: true, subtree: true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
})();
