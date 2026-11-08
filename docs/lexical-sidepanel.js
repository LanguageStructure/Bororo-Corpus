/* Painel lexical compartilhado dos leitores documentais CorBo. */
(()=>{'use strict';
const style=document.createElement('style');style.textContent=`
#corboLexSide{position:fixed;z-index:2200;right:14px;top:14px;bottom:14px;width:min(390px,calc(100vw - 28px));overflow:auto;background:#fff;color:#202624;border:1px solid #d8e1db;border-radius:12px;padding:22px;box-shadow:0 12px 38px #0002;font:15px/1.6 system-ui,sans-serif}
#corboLexSide[hidden]{display:none}#corboLexSide .close{float:right;border:0;background:transparent;font-size:24px;cursor:pointer}#corboLexSide h2{font:600 25px Georgia,serif;margin:0 30px 16px 0}#corboLexSide .label{font-size:12px;color:#6d7672;margin-top:14px}
@media(min-width:851px){body.corbo-lex-open main{margin-right:410px;max-width:none}}
@media(max-width:850px){#corboLexSide{top:auto;bottom:0;left:0;right:0;max-height:65vh}}`;document.head.append(style);
const panel=document.createElement('aside');panel.id='corboLexSide';panel.hidden=true;panel.setAttribute('aria-label','Informações lexicais');panel.innerHTML='<button class="close" type="button" aria-label="Fechar painel">×</button><div id="corboLexContent"></div>';document.body.append(panel);
const content=panel.querySelector('#corboLexContent'),norm=s=>String(s??'').normalize('NFC').toLocaleLowerCase('pt-BR'),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),uniq=a=>[...new Set(a.filter(Boolean))];
let annotations=null,morphology=null,seq=0;
function close(){panel.hidden=true;document.body.classList.remove('corbo-lex-open')}
panel.querySelector('.close').onclick=close;document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
async function load(url){let r=await fetch(url);if(!r.ok)throw Error('HTTP '+r.status);return r.json()}
async function open(word){let current=++seq;panel.hidden=false;document.body.classList.add('corbo-lex-open');content.innerHTML='<h2>'+esc(word)+'</h2><p>Consultando anotações…</p>';
try{annotations??=load('./data/dictionary-annotations.json').catch(()=>[]);morphology??=load('./data/morphology.json').catch(()=>({}));let [a,m]=await Promise.all([annotations,morphology]);if(current!==seq)return;
let entries=(Array.isArray(a)?a:[]).filter(x=>norm(x.form)===norm(word)),aggregate=(m.relacoes_lexicais||[]).find(x=>norm(x.form)===norm(word));
let lemmas=uniq([...entries.map(x=>x.lemma),...(aggregate?.lemmas||[]).map(x=>x.value)]),upos=uniq([...entries.map(x=>x.upos),...(aggregate?.upos||[]).map(x=>x.value)]).map(x=>window.CorBoUDpt?.classe(x)||x),gloss=uniq([...(aggregate?.glossas||[]).map(x=>x.value)]);
let row=(label,values)=>values.length?'<div class="label">'+label+'</div><div>'+values.map(esc).join(' · ')+'</div>':'';
content.innerHTML='<h2>'+esc(word)+'</h2>'+row('Tradução / glosa disponível',gloss)+row('Classe gramatical',upos)+row('Lema',lemmas)+(!lemmas.length&&!upos.length&&!gloss.length?'<p>Sem informação lexical registrada.</p>':'')+'<p><a href="word.html?form='+encodeURIComponent(word)+'">Ver todas as ocorrências</a></p>';
}catch{if(current===seq)content.innerHTML='<h2>'+esc(word)+'</h2><p>Não foi possível consultar as anotações.</p><a href="word.html?form='+encodeURIComponent(word)+'">Ver ocorrências</a>'}}
document.addEventListener('click',e=>{const el=e.target.closest('#units .word, #entries .word');if(!el)return;e.preventDefault();e.stopImmediatePropagation();open(el.textContent.trim())},true);
})();