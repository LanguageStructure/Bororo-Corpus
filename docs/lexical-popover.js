/* Carrega o painel lexical único (lexical-panel.js). Mantido para as páginas
   que ainda referenciam lexical-popover.js ou lexical-sidepanel.js. */
(() => {
  if (window.CorBoLexPanel || document.querySelector('script[data-corbo-lex]')) return;
  const s = document.createElement('script');
  s.src = 'lexical-panel.js';
  s.dataset.corboLex = '1';
  document.head.append(s);
})();
