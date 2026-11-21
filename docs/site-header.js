/* Cabeçalho único do site CorBo.
   Substitui o primeiro <header> da página (ou cria um) por uma navegação
   agrupada e igual em todas as páginas. Para editar o menu, altere MENU. */
(() => {
  'use strict';
  const MENU = [
    ['Corpus', [
      ['catalogo.html', 'Catálogo de textos'],
      ['boe-ero.html', 'Boe Ero'],
      ['oieigo.html', 'Oiegos'],
      ['catalogo.html#biblicos', 'Textos bíblicos'],
      ['dicionario.html', 'Dicionário'],
      ['vocabulario-tematico.html', 'Vocabulário temático'],
    ]],
    ['Ferramentas', [
      ['search.html', 'Busca e concordância'],
      ['word-search.html', 'Busca de palavras'],
      ['forms.html', 'Análise de formas'],
      ['morphemes.html', 'Morfemas'],
      ['morph-index.html', 'Índice morfológico'],
      ['relations.html', 'Relações linguísticas'],
      ['reviewed-paradigms.html', 'Paradigmas revisados'],
      ['ud.html', 'Visualizador CoNLL-U'],
      ['tokenizer.html', 'Tokenizador'],
      ['generator.html', 'Gerador'],
    ]],
    ['Estatísticas', [
      ['statistics.html', 'Estatísticas e n-grams'],
      ['coverage.html', 'Cobertura da anotação'],
      ['keywords.html', 'Palavras-chave'],
      ['lexical-growth.html', 'Crescimento lexical'],
    ]],
    ['Aprender', [
      ['aprendizagem.html', 'Aprendizagem'],
      ['exercicios.html', 'Exercícios'],
      ['como-usar.html', 'Como usar o site'],
    ]],
    ['about.html', 'Sobre'],
  ];

  const css = `
  .cb-header{background:#fff!important;color:#202624!important;border-bottom:1px solid #e3e7e4;position:sticky;top:0;z-index:2100;padding:0!important;margin:0!important;display:block!important;max-width:none!important;font:15px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}
  .cb-header *{box-sizing:border-box}
  .cb-bar{max-width:1200px;margin:auto;padding:12px 24px;display:flex;align-items:center;gap:24px}
  .cb-brand{color:#202624;text-decoration:none;display:flex;flex-direction:column;line-height:1.1;margin-right:auto}
  .cb-brand b{font:700 22px Georgia,serif}.cb-brand small{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:#6d7672}
  .cb-nav{display:flex;align-items:center;gap:4px}
  .cb-nav > a,.cb-group > button{font:inherit;color:#33403a;background:none;border:0;padding:8px 12px;border-radius:8px;cursor:pointer;text-decoration:none;white-space:nowrap}
  .cb-nav > a:hover,.cb-group > button:hover,.cb-group.open > button{background:#eef3f1}
  .cb-nav .cb-current{color:#527066;font-weight:600}
  .cb-group{position:relative}
  .cb-group > button::after{content:"▾";font-size:11px;margin-left:5px;opacity:.6}
  .cb-menu{display:none;position:absolute;right:0;top:calc(100% + 6px);min-width:230px;background:#fff;border:1px solid #e3e7e4;border-radius:10px;box-shadow:0 12px 28px rgba(0,0,0,.1);padding:6px}
  .cb-group.open .cb-menu{display:block}
  .cb-menu a{display:block;padding:8px 12px;border-radius:7px;color:#202624;text-decoration:none}
  .cb-menu a:hover{background:#eef3f1}.cb-menu a.cb-current{color:#527066;font-weight:600}
  .cb-toggle{display:none;font-size:22px;background:none;border:0;cursor:pointer;padding:4px 8px}
  @media(max-width:820px){
    .cb-toggle{display:block}.cb-nav{display:none;position:absolute;left:0;right:0;top:100%;background:#fff;border-bottom:1px solid #e3e7e4;flex-direction:column;align-items:stretch;padding:8px 16px 14px}
    .cb-header.open .cb-nav{display:flex}.cb-menu{position:static;box-shadow:none;border:0;padding:0 0 0 12px}.cb-group > button{width:100%;text-align:left}
  }`;
  const page = (location.pathname.split('/').pop() || 'index.html');
  const isCur = href => href.split('#')[0] === page;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

  function build() {
    if (document.querySelector('.cb-header')) return;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.append(style);
    const header = document.createElement('header');
    header.className = 'cb-header';
    let nav = '';
    for (const item of MENU) {
      if (typeof item[1] === 'string') {
        nav += `<a href="${item[0]}"${isCur(item[0]) ? ' class="cb-current" aria-current="page"' : ''}>${esc(item[1])}</a>`;
      } else {
        const cur = item[1].some(([h]) => isCur(h));
        nav += `<div class="cb-group"><button type="button" aria-expanded="false"${cur ? ' class="cb-current"' : ''}>${esc(item[0])}</button><div class="cb-menu">` +
          item[1].map(([h, t]) => `<a href="${h}"${isCur(h) ? ' class="cb-current" aria-current="page"' : ''}>${esc(t)}</a>`).join('') + '</div></div>';
      }
    }
    header.innerHTML = `<div class="cb-bar"><a class="cb-brand" href="./"><b>CorBo</b><small>Corpus da Língua Bororo</small></a>` +
      `<button class="cb-toggle" type="button" aria-label="Abrir menu">☰</button><nav class="cb-nav" aria-label="Navegação principal">${nav}</nav></div>`;
    const old = document.body.querySelector(':scope > header');
    if (old) old.replaceWith(header); else document.body.prepend(header);

    const groups = [...header.querySelectorAll('.cb-group')];
    const closeAll = except => groups.forEach(g => { if (g !== except) { g.classList.remove('open'); g.firstElementChild.setAttribute('aria-expanded', 'false'); } });
    groups.forEach(g => g.firstElementChild.addEventListener('click', e => {
      e.stopPropagation();
      const open = !g.classList.contains('open');
      closeAll(g);
      g.classList.toggle('open', open);
      g.firstElementChild.setAttribute('aria-expanded', String(open));
    }));
    header.querySelector('.cb-toggle').addEventListener('click', () => header.classList.toggle('open'));
    document.addEventListener('click', () => closeAll());
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeAll(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();
