/* Ferramentas por unidade nos leitores: link permanente (#id) e "sugerir correção"
   (abre uma issue no GitHub já preenchida). Funciona com qualquer elemento .unit;
   quando a unidade não tem id, usa o identificador escrito na primeira linha do cartão. */
(() => {
  'use strict';
  if (window.CorBoUnitTools) return;
  window.CorBoUnitTools = true;
  const en = document.documentElement.lang.startsWith('en');
  const REPO = 'https://github.com/LanguageStructure/Bororo-Corpus/issues/new';
  const style = document.createElement('style');
  style.textContent = `
  .cb-unit-tools{display:flex;gap:14px;justify-content:flex-end;margin-top:10px;font:13px system-ui,sans-serif;opacity:.55;transition:opacity .15s}
  .unit:hover .cb-unit-tools,.cb-unit-tools:focus-within{opacity:1}
  .cb-unit-tools a,.cb-unit-tools button{color:#527066;background:none;border:0;padding:0;font:inherit;cursor:pointer;text-decoration:none}
  .cb-unit-tools a:hover,.cb-unit-tools button:hover{text-decoration:underline}
  .unit.cb-target{outline:2px solid #527066;outline-offset:4px;border-radius:8px}
  @media (hover:none){.cb-unit-tools{opacity:1}}`;
  document.head.append(style);

  const idOf = el => {
    if (el.id) return el.id;
    const first = el.firstElementChild?.textContent || '';
    const m = first.match(/([A-Za-z][\w.:-]*\d[\w.:-]*)\s*$/);
    if (m && !document.getElementById(m[1])) { el.id = m[1]; return m[1]; }
    return '';
  };
  const textOf = el => {
    const t = el.querySelector('.bor, .b, [lang="bor"]') || el;
    return (t.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 400);
  };

  function decorate(el) {
    if (el.dataset.cbTools) return;
    el.dataset.cbTools = '1';
    const id = idOf(el);
    if (!id) return;
    const url = location.origin + location.pathname + '#' + encodeURIComponent(id);
    const bar = document.createElement('div');
    bar.className = 'cb-unit-tools';
    const title = `${en ? 'Correction' : 'Correção'}: ${id}`;
    const body = [
      `**${en ? 'Unit' : 'Unidade'}:** ${id}`, `**${en ? 'Page' : 'Página'}:** ${url}`, '',
      `**${en ? 'Current text' : 'Texto atual'}:**`, '> ' + textOf(el), '',
      `**${en ? 'Proposed correction' : 'Correção proposta'}:**`, '', '',
      `**${en ? 'Source or justification' : 'Fonte ou justificativa'}:**`, ''].join('\n');
    const issue = `${REPO}?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
    bar.innerHTML = `<button type="button" data-a="copy" title="${en ? 'Copy permanent link' : 'Copiar link permanente'}">🔗 ${en ? 'Link' : 'Link'}</button>` +
      `<a href="${issue}" target="_blank" rel="noopener" title="${en ? 'Opens a GitHub issue' : 'Abre uma issue no GitHub'}">✎ ${en ? 'Suggest a correction' : 'Sugerir correção'}</a>`;
    bar.querySelector('[data-a=copy]').addEventListener('click', async e => {
      e.stopPropagation();
      history.replaceState(null, '', '#' + encodeURIComponent(id));
      try { await navigator.clipboard.writeText(url); e.target.textContent = en ? '✓ Copied' : '✓ Copiado'; }
      catch { e.target.textContent = url; }
      setTimeout(() => { e.target.textContent = '🔗 Link'; }, 2000);
    });
    el.append(bar);
  }

  let targeted = false;
  function scan() {
    document.querySelectorAll('.unit').forEach(decorate);
    const hash = decodeURIComponent(location.hash.slice(1));
    if (!targeted && hash) {
      const t = document.getElementById(hash);
      if (t && t.classList.contains('unit')) {
        targeted = true;
        t.classList.add('cb-target');
        t.scrollIntoView({block: 'center'});
      }
    }
  }
  let pending = false;
  new MutationObserver(() => { if (!pending) { pending = true; requestAnimationFrame(() => { pending = false; scan(); }); } })
    .observe(document.documentElement, {childList: true, subtree: true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
  addEventListener('hashchange', () => { targeted = false; scan(); });
})();
