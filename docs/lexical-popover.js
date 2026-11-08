(function(){
'use strict';
const style=document.createElement('style');
style.textContent=`
.corbo-lex-pop{position:fixed;right:12px;top:12px;bottom:12px;z-index:1200;background:#fff;color:#202624;border:1px solid #dce5df;border-radius:12px;padding:20px;width:min(420px,calc(100vw - 24px));overflow-y:auto;box-shadow:0 12px 35px #0002;font:15px/1.5 system-ui;box-sizing:border-box}
.corbo-lex-pop[hidden]{display:none}.corbo-lex-pop h3{font:700 25px Georgia,serif;margin:0 28px 12px 0;overflow-wrap:anywhere}.corbo-lex-pop h4{margin:18px 0 6px;font-size:15px;border-bottom:1px solid #e3e7e4;padding-bottom:5px}.corbo-lex-pop .label{font-size:12px;color:#6d7672}.corbo-lex-pop .field{margin:10px 0}.corbo-lex-pop .field .value{overflow-wrap:anywhere}.corbo-lex-pop .close{position:absolute;right:12px;top:8px;background:none;border:0;font-size:24px;cursor:pointer}.corbo-lex-pop a{color:#527066}.corbo-lex-pop .muted{color:#6d7672;font-size:13px}.corbo-lex-pop .count{font-size:22px;font-weight:700}
@media(min-width:1000px){body.corbo-lex-open{padding-right:440px}body.corbo-lex-open .layout{max-width:none}body.corbo-lex-open .layout article{min-width:0}}
@media(max-width:700px){.corbo-lex-pop{top:auto;bottom:0;right:0;left:0;width:100%;max-height:70vh;border-radius:12px 12px 0 0}}
`;
document.head.appendChild(style);
const box=document.createElement('aside');box.className='corbo-lex-pop';box.hidden=true;box.setAttribute('aria-label','Informações lexicais');box.innerHTML='<button class="close" type="button" aria-label="Fechar painel">×</button><div class="body" aria-live="polite"></div>';document.body.appendChild(box);
const close=()=>{box.hidden=true;document.body.classList.remove('corbo-lex-open')};box.querySelector('.close').addEventListener('click',close);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
const norm=s=>String(s||'').normalize('NFC').toLocaleLowerCase('pt-BR');
const unique=xs=>[...new Set(xs.filter(x=>x!==null&&x!==undefined&&String(x).trim()&&x!=='_').map(String))];
const vals=(obj,key)=>Array.isArray(obj?.[key])?obj[key].map(x=>typeof x==='string'?x:x.value):[];
const field=(label,values)=>{const a=unique(Array.isArray(values)?values:[values]);return a.length?'<div class="field"><div class="label">'+esc(label)+'</div><div class="value">'+a.map(esc).join(' · ')+'</div></div>':''};
const fetchJSON=async(path,fallback)=>{try{const r=await fetch(path);return r.ok?await r.json():fallback}catch(_){return fallback}};
let cache;
function data(){return cache||(cache=Promise.all([
fetchJSON('./data/morphology.json',{}),
fetchJSON('./data/dictionary-annotations.json',[]),
fetchJSON('./data/grammatical-index.json',{}),
fetchJSON('./data/corbo-stats.json',{}),
fetchJSON('./data/dicionario-bororo-publico.json',{entries:[]})
]).then(([m,d,g,s,dict])=>({m,d,g,s,dict})))}
let sequence=0;
async function show(word){
const seq=++sequence;box.hidden=false;document.body.classList.add('corbo-lex-open');
const body=box.querySelector('.body');body.innerHTML='<h3>'+esc(word)+'</h3><p class="muted">Consultando os índices…</p>';
try{
const {m,d,g,s,dict}=await data();if(seq!==sequence||box.hidden)return;
const relation=(m.relacoes_lexicais||[]).find(x=>norm(x.form)===norm(word));
const gram=g.lexicon?.[norm(word)]||{};
const annotated=(Array.isArray(d)?d:[]).filter(x=>norm(x.form)===norm(word));
const lemmas=unique([...vals(relation,'lemmas'),...annotated.map(x=>x.lemma),...(gram.analyses||[]).map(x=>x.lemma)]);
const classes=unique([...vals(relation,'upos'),...annotated.map(x=>x.upos),...(gram.analyses||[]).map(x=>x.upos)]).map(x=>window.CorBoUDpt?.classe(x)||x);
const glosses=unique(vals(relation,'glossas'));
const topForms=Array.isArray(s.top_forms)?s.top_forms:[];
const stat=topForms.find(x=>norm(x.form)===norm(word));
const freq=stat?.frequency??gram.frequency??relation?.frequency;
const editorial=(m.analises_editoriais||[]).filter(x=>norm(x.form)===norm(word));
const analyses=(gram.analyses||[]).slice(0,5);
const lemmaFreq=lemmas.length?Object.entries(g.lexicon||{}).reduce((n,[form,item])=>n+(item.analyses||[]).reduce((sum,a)=>sum+(lemmas.some(l=>norm(l)===norm(a.lemma))?Number(a.frequency||0):0),0),0):null;
let html='<h3>'+esc(word)+'</h3><h4>Identificação</h4>';
html+=field('Forma',word)+field('Lema',lemmas)+field('Classe gramatical',classes);
const dictionaryEntries=Array.isArray(dict.entries)?dict.entries:[];
const keys=unique([word,...lemmas]).map(norm);
const matches=dictionaryEntries.filter(x=>keys.includes(norm(x.entry))||keys.includes(norm(x.lemma_key)));
html+='<h4>Dicionário Bororo</h4>';
if(matches.length){
 for(const entry of matches.slice(0,12)){
  html+='<div class="field"><strong>'+esc(entry.entry)+'</strong>';
  html+=field('Transcrição fonética',entry.ipa)+field('Classe lexicográfica',entry.pos)+field('Definição',entry.definition)+field('Exemplo do dicionário',entry.example_sent)+field('Observações',entry.comment);
  html+='</div>';
 }
 if(matches.length>12)html+='<p class="muted">Outras entradas disponíveis na consulta completa.</p>';
}else html+='<p class="muted">Nenhuma entrada correspondente à forma ou aos lemas identificados.</p>';
html+='<p><a href="dicionario.html?lemma='+encodeURIComponent(lemmas[0]||word)+'">Consultar o dicionário completo →</a></p>';
if(glosses.length)html+=field('Glosas registradas no CoNLL-U (não equivalem necessariamente à tradução)',glosses);
html+='<h4>Frequência</h4>';
html+=freq!==undefined?field('Ocorrências da forma',Number(freq).toLocaleString('pt-BR')):'<p class="muted">Frequência da forma indisponível.</p>';
if(lemmaFreq!==null)html+=field('Ocorrências dos lemas identificados (anotações CoNLL-U)',lemmaFreq.toLocaleString('pt-BR'));
html+='<h4>Morfologia e sintaxe</h4>';
if(analyses.length){
html+=field('Traços gramaticais documentados',analyses.map(x=>x.feats));
}
for(const a of editorial.slice(0,3)){
html+=field('Segmentação editorial',a.segmentation)+field('Morfemas',String(a.morphemes||'').replaceAll('|',' · '))+field('Glosas editoriais',String(a.gloss||'').replaceAll('|',' · '));
}
html+=field('Classe detalhada',vals(relation,'pos_detalhada'))+field('Classe de posse',vals(relation,'classes_posse'))+field('Proclíticos',vals(relation,'procliticos'));
html+='<p class="muted">Relações sintáticas por ocorrência: consulte a visualização UD da frase.</p>';
html+='<p><a href="word.html?form='+encodeURIComponent(word)+'">Ver ocorrências e concordâncias →</a></p>';
body.innerHTML=html;
}catch(e){if(seq===sequence)body.innerHTML='<h3>'+esc(word)+'</h3><p>Consulta indisponível.</p>'}
}
document.addEventListener('click',e=>{const w=e.target.closest('.word');if(w){e.preventDefault();show(w.textContent.trim())}});
document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
})();
