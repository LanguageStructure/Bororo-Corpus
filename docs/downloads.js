/* Página Downloads (PT/EN): lê data/downloads.json (scripts/build_downloads.py). */
(async () => {
  'use strict';
  const en = document.documentElement.lang.startsWith('en');
  const box = document.getElementById('downloads');
  const T = en ? {
    textos: 'Texts', anotacao: 'Annotation (CoNLL-U)', lexico: 'Lexicon and indexes', documentacao: 'Documentation',
    file: 'File', fmt: 'Format', size: 'Size', none: 'Download list unavailable.', zip: 'Whole repository (ZIP)',
    zenodo: 'Versioned archive on Zenodo (recommended for citation)', gen: 'List generated on',
  } : {
    textos: 'Textos', anotacao: 'Anotação (CoNLL-U)', lexico: 'Léxico e índices', documentacao: 'Documentação',
    file: 'Arquivo', fmt: 'Formato', size: 'Tamanho', none: 'Lista de downloads indisponível.', zip: 'Repositório completo (ZIP)',
    zenodo: 'Arquivo versionado no Zenodo (recomendado para citação)', gen: 'Lista gerada em',
  };
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const size = b => b == null ? '–' : b > 1e6 ? (b / 1e6).toFixed(1).replace('.', en ? '.' : ',') + ' MB' : Math.max(1, Math.round(b / 1e3)) + ' kB';
  let d;
  try { const r = await fetch('./data/downloads.json', {cache: 'no-cache'}); if (!r.ok) throw 0; d = await r.json(); }
  catch { box.innerHTML = `<p class="muted">${T.none}</p>`; return; }
  const groups = ['textos', 'anotacao', 'lexico', 'documentacao'];
  let h = '';
  for (const g of groups) {
    const files = d.files.filter(f => f.group === g);
    if (!files.length) continue;
    h += `<h2>${T[g]}</h2><div class="dl-list">`;
    for (const f of files) {
      h += `<div class="dl-item"><div><a class="dl-name" href="${esc(f.url)}" download>${esc(f.name)}</a>` +
        `<span class="dl-fmt">${esc(f.format)}</span><span class="dl-size">${size(f.bytes)}</span></div>` +
        `<p>${esc(en ? f.en : f.pt)}</p>${(en ? f.counts_en : f.counts_pt) ? `<p class="muted">${esc(en ? f.counts_en : f.counts_pt)}</p>` : ''}</div>`;
    }
    h += '</div>';
  }
  h += `<h2>${en ? 'Complete packages' : 'Pacotes completos'}</h2><div class="dl-list">` +
    `<div class="dl-item"><a class="dl-name" href="https://doi.org/${esc(d.doi)}">DOI ${esc(d.doi)}</a><p>${T.zenodo}</p></div>` +
    `<div class="dl-item"><a class="dl-name" href="${esc(d.repository_zip)}">${T.zip}</a><p>${en ? 'Current state of the main branch, including scripts and sources.' : 'Estado atual do ramo principal, com scripts e fontes.'}</p></div></div>` +
    `<p class="muted">${T.gen} ${esc(d.generated)} · ${esc(d.license)}</p>`;
  box.innerHTML = h;
})();
