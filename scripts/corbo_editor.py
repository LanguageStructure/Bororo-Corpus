#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Editor local do CorBo. Acesso somente em 127.0.0.1."""
from __future__ import annotations
import csv,json,re,subprocess,sys,threading,webbrowser
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from build_corpus_indexes import conllu_relations,CONLLU,main as build_indexes
ROOT=Path(__file__).resolve().parents[1]
FILES={'coqueiro':ROOT/'CorBo_vNext/texts/coqueiro/coqueiro_parallel.tsv','hm':ROOT/'CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv','adugo':ROOT/'CorBo_vNext/texts/adugo-biri/adugo_biri_parallel.tsv','boeero':ROOT/'CorBo_vNext/texts/boe-ero/boe_ero_parallel.tsv','bakarudoge':ROOT/'CorBo_vNext/texts/bakarudoge/bakarudoge_documentary.tsv','bibliaoral':ROOT/'CorBo_vNext/texts/biblia-oral/biblia_oral_interlinear.tsv','paulinho':ROOT/'CorBo_vNext/texts/paulinho/paulinho_interlinear.tsv','oieigo':ROOT/'CorBo_vNext/texts/oieigo/oieigo_parallel.tsv','morph':ROOT/'CorBo_vNext/annotations/morphology.tsv'}
OIEIGO_COMMENT=ROOT/'CorBo_vNext/texts/oieigo/comment.txt'
BAK_EDITS=ROOT/'CorBo_vNext/texts/bakarudoge/bakarudoge_linear_edits.tsv'
BIBLES={'jonas':('Jonas',ROOT/'CorBo/Corpus_Files/bíblia/jonas_2-orthophon.txt',ROOT/'CorBo_vNext/texts/biblia/jonas_review.tsv','JON'),'ageu':('Ageu',ROOT/'CorBo/Corpus_Files/bíblia/ageu_2-orthophon.txt',ROOT/'CorBo_vNext/texts/biblia/ageu_review.tsv','AGE'),'cantico':('Cântico dos Cânticos',ROOT/'CorBo/Corpus_Files/bíblia/cantico_dos_canticos_2-orthophon.txt',ROOT/'CorBo_vNext/texts/biblia/cantico_review.tsv','CAN')}
def bible_editor_units(key):
 title,src,review,prefix=BIBLES[key];paras=[x.strip() for x in re.split(r'\n\s*\n',src.read_text(encoding='utf-8')) if x.strip()];ed={r['id']:r for r in read_tsv_path(review)} if review.exists() else {};return [{'id':f'BOR-CORBO-BIB-{prefix}-{i:04d}','source':s,'reviewed':ed.get(f'BOR-CORBO-BIB-{prefix}-{i:04d}',{}).get('reviewed',''),'portuguese':ed.get(f'BOR-CORBO-BIB-{prefix}-{i:04d}',{}).get('portuguese','')} for i,s in enumerate(paras,1)]
def read_tsv_path(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def save_bible(key,body):
 title,src,p,prefix=BIBLES[key];rows=read_tsv_path(p) if p.exists() else [];uid=str(body.get('id','')).strip();m=next((r for r in rows if r.get('id')==uid),None);data={'id':uid,'reviewed':str(body.get('reviewed','')).strip(),'portuguese':str(body.get('portuguese','')).strip()};m.update(data) if m else rows.append(data);tmp=p.with_suffix('.tsv.tmp');
 with tmp.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['id','reviewed','portuguese'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 tmp.replace(p)
BUILD=ROOT/'scripts/build_corpus_indexes.py'; HOST='127.0.0.1'; PORT=8765
MF=['form','segmentation','morphemes','gloss','status','note']
def read_rows(c):
 with FILES[c].open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write_rows(c,rows,fields=None):
 p=FILES[c];tmp=p.with_suffix('.tsv.tmp');fields=fields or [k for k in rows[0].keys() if k is not None]
 clean=[{k:r.get(k,'') for k in fields} for r in rows]
 with tmp.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(clean)
 tmp.replace(p)
def vals(a):return ', '.join(x['value'] for x in (a or []))
def bakarudoge_units():
 docs=read_rows('bakarudoge');ed={}
 if BAK_EDITS.exists():
  with BAK_EDITS.open(encoding='utf-8',newline='') as f:ed={r['id']:r for r in csv.DictReader(f,delimiter='\t')}
 out=[]
 trans_heads=('interpretação','interpretacao','versão portuguesa desta lenda','versao portuguesa desta lenda','versão portuguesa','versao portuguesa')
 stop_heads=('dados culturais','notas culturais','explicação','explicacao')
 num_re=re.compile(r'^\\s*(\\d{1,3})[.)]?\\s*(.*)$')
 for d in docs:
  source=[];translation=[];mode='source'
  for raw in (d.get('documentary_content') or '').splitlines():
   line=raw.strip()
   if not line:continue
   low=line.casefold().rstrip(':')
   if low in ('vocabulário','vocabulario'):
    # Vocabulary separates source from a later Portuguese version; ignore vocabulary itself.
    mode='between';continue
   if any(low.startswith(x) for x in trans_heads):
    mode='translation';continue
   if any(low.startswith(x) for x in stop_heads):
    if mode=='translation':break
    mode='between';continue
   if mode=='source':source.append(line)
   elif mode=='translation':translation.append(line)
  def source_units(lines):
   rows=[]
   for line in lines:
    m=num_re.match(line)
    if m:rows.append({'number':m.group(1),'text':m.group(2).strip()})
    elif rows:
     # Unnumbered source lines are independent interlinear units, never appended to the previous numbered paragraph.
     rows.append({'number':'','text':line})
    else:rows.append({'number':'','text':line})
   return rows
  def translation_units(lines):
   rows=[]
   for line in lines:
    m=num_re.match(line)
    if m:rows.append({'number':m.group(1),'text':m.group(2).strip()})
    else:rows.append({'number':'','text':line})
   return rows
  src=source_units(source);tr=translation_units(translation)
  numbered_pt=any(x['number'] for x in tr)
  bynum={}
  if numbered_pt:
   for x in tr:
    if x['number'] and x['number'] not in bynum:bynum[x['number']]=x['text']
  ordered=[x['text'] for x in tr if x['text']]
  for n,x in enumerate(src,1):
   uid=f"{d['id'].replace('-BAK-','-BKD-')}-{n:03d}";m=ed.get(uid,{})
   docpt=bynum.get(x['number'],'') if numbered_pt else ''
   candidate=(ordered[n-1] if (not numbered_pt and n<=len(ordered)) else '')
   out.append({'id':uid,'myth_number':d.get('text_number',''),'title':d.get('title',''),'source_number':x['number'],'source':x['text'],'reviewed':m.get('reviewed',''),'linear_portuguese':m.get('linear_portuguese','') or docpt,'documentary_translation':docpt,'translation_candidate':candidate,'editorial_note':m.get('editorial_note','')})
 return out
def save_bakarudoge_edit(body):
 uid=str(body.get('id','')).strip();rows=[]
 fields=['id','reviewed','linear_portuguese','editorial_note']
 if BAK_EDITS.exists():
  with BAK_EDITS.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
 m=next((r for r in rows if r.get('id')==uid),None)
 data={'id':uid,'reviewed':str(body.get('reviewed','')).strip(),'linear_portuguese':str(body.get('linear_portuguese','')).strip(),'editorial_note':str(body.get('editorial_note','')).strip()}
 if m:m.update(data)
 else:rows.append(data)
 BAK_EDITS.parent.mkdir(parents=True,exist_ok=True);tmp=BAK_EDITS.with_suffix('.tsv.tmp')
 with tmp.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 tmp.replace(BAK_EDITS)

def morph_rows():
 ed={r['form'].casefold():r for r in read_rows('morph')}
 out=[]
 for r in conllu_relations(CONLLU):
  e=ed.pop(r['form'].casefold(),{})
  out.append({'form':r['form'],'frequency':r['frequency'],'lemma':vals(r['lemmas']),'classe':vals(r['pos_detalhada']) or vals(r['upos']),'glossa_conllu':vals(r['glossas']),'classe_posse':vals(r['classes_posse']),'proclitico':vals(r['procliticos']),'segmentation':e.get('segmentation',''),'morphemes':e.get('morphemes',''),'gloss':e.get('gloss',''),'status':e.get('status',''),'note':e.get('note',''),'editorial':bool(e)})
 for e in ed.values():out.append({'form':e['form'],'frequency':0,'lemma':'','classe':'','glossa_conllu':'','classe_posse':'','proclitico':'','segmentation':e.get('segmentation',''),'morphemes':e.get('morphemes',''),'gloss':e.get('gloss',''),'status':e.get('status',''),'note':e.get('note',''),'editorial':True})
 return out
PAGE=r'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Editor do CorBo</title><style>:root{font-family:system-ui,sans-serif;color:#202124;background:#f6f4ef}*{box-sizing:border-box}body{margin:0}header{padding:18px 26px;background:#fff;border-bottom:1px solid #ddd;display:flex;gap:24px;align-items:center}h1{margin:0;font:25px Georgia,serif}select,input,textarea{font:inherit;border:1px solid #bbb;border-radius:6px;padding:10px;background:#fff}select{min-width:190px}.grid{display:grid;grid-template-columns:minmax(320px,32%) 1fr;height:calc(100vh - 75px)}aside{padding:18px;border-right:1px solid #ddd;overflow:auto;background:#fff}aside input{width:100%}main{padding:26px;overflow:auto}.unit{padding:9px 6px;border-bottom:1px solid #eee;cursor:pointer}.unit:hover,.unit.on{background:#f0eee7}.id{font:12px ui-monospace,monospace;color:#666}.bor{font-family:Georgia,serif}.card{max-width:1050px;background:#fff;border:1px solid #ddd;border-radius:8px;padding:22px}.cols{display:grid;grid-template-columns:1fr 1fr;gap:18px}.published{padding:12px;background:#f7f7f7;border-radius:6px;white-space:pre-wrap;min-height:48px}.label{font-weight:650;margin:15px 0 6px}textarea,input.field,select.field{width:100%}textarea{min-height:100px}.wide{grid-column:1/-1}button{padding:10px 14px;border:0;border-radius:6px;cursor:pointer;font-weight:650}.primary{background:#222;color:#fff}.secondary{background:#e7e5df;margin-left:8px}.actions{margin-top:20px}.status{margin-left:12px;color:#555}.notice{padding:10px 12px;background:#fff7d6;border-radius:6px;margin:12px 0}.source{background:#edf3ee;padding:14px;border-radius:7px;margin-bottom:18px}@media(max-width:800px){.grid{display:block;height:auto}.cols{grid-template-columns:1fr}aside{max-height:35vh}}</style></head><body><header><h1>Editor do CorBo</h1><select id="corpus"><option value="coqueiro">Coqueiro</option><option value="hm">História Mítica</option><option value="adugo">Adugo Biri</option><option value="boeero">Boe Ero</option><option value="bakarudoge">Bakarudoge</option><option value="jonas">Bíblia — Jonas</option><option value="ageu">Bíblia — Ageu</option><option value="cantico">Bíblia — Cântico dos Cânticos</option><option value="bibliaoral">Criação do mundo — narrativa Bororo</option><option value="paulinho">História da Corujinha — Tagogorogu</option><option value="oieigo">Oieigo Jiwu Bakaru</option><option value="morph">Morfologia</option></select><span class="id">local · 127.0.0.1</span></header><div class="grid"><aside><input id="q" placeholder="Buscar (diferencia maiúsculas/minúsculas)"><div id="list"></div></aside><main><div id="empty">Selecione uma entrada.</div><div id="card" class="card" hidden><div class="id" id="uid"></div><div id="normal"><div class="cols"><section><div class="label" id="l1"></div><div class="published bor" id="a"></div></section><section><div class="label" id="l2"></div><div class="published" id="b"></div></section><section class="wide" id="docwrap" hidden><div class="label">Metadados documentais</div><div class="source"><div><b>Número no Bororo:</b> <span id="snum"></span> · <b>Número na tradução:</b> <span id="tnum"></span></div><div id="notewrap" hidden><b>Nota editorial:</b> <span id="ednote"></span></div></div></section><section class="wide"><div class="label" id="editlabel"></div><textarea id="edit"></textarea></section><section class="wide" id="docptwrap" hidden><div class="label" id="docptlabel">Tradução portuguesa documental</div><div class="published" id="docpt"></div></section><section class="wide" id="porwrap"><div class="label">Português revisado</div><textarea id="pedit"></textarea></section><section class="wide" id="commentwrap" hidden><div class="label">Comentário final do texto</div><textarea id="textcomment"></textarea><div class="muted">Comentário documental exibido após a tradução, separado das unidades paralelas.</div></section></div></div><div id="morphform" hidden><div class="notice">Os dados abaixo vêm do CoNLL-U e permanecem preservados. Sua revisão é registrada separadamente como camada editorial.</div><div class="source"><div class="cols"><div><b>Forma:</b> <span id="cf"></span></div><div><b>Frequência:</b> <span id="freq"></span></div><div><b>Lema:</b> <span id="cl"></span></div><div><b>Classe gramatical:</b> <span id="cc"></span></div><div><b>Glossa:</b> <span id="cg"></span></div><div><b>Classe de posse:</b> <span id="cp"></span></div><div><b>Proclítico:</b> <span id="cpr"></span></div><div><b>Fonte:</b> CoNLL-U</div></div></div><h2>Revisão editorial</h2><div class="cols"><section><div class="label">Segmentação</div><input class="field" id="ms"></section><section><div class="label">Morfemas (separados por |)</div><input class="field" id="mm"></section><section><div class="label">Glosas editoriais (separadas por |)</div><input class="field" id="mg"></section><section><div class="label">Estado da análise</div><select class="field" id="mst"><option value="">Sem revisão</option><option value="confirmed">Confirmada</option><option value="partial">Parcial</option><option value="provisional">Provisória</option></select></section><section class="wide"><div class="label">Nota</div><textarea id="mn"></textarea></section></div></div><div class="actions"><button class="primary" id="save">Salvar revisão</button><button class="secondary" id="reset">Restaurar campos</button><span class="status" id="status"></span></div><div class="actions"><button class="secondary" id="build">Validar e regenerar dados</button><span class="status" id="buildstatus"></span></div></div></main></div><script>let units=[],current=null;const $=x=>document.getElementById(x),kind=()=>$('corpus').value;function esc(s){let d=document.createElement('div');d.textContent=s||'';return d.innerHTML}async function load(){let r=await fetch('/api/units?corpus='+kind()),x=await r.json();if(!r.ok){$('list').innerHTML='<div class=notice>'+esc(x.error)+'</div>';return}units=x;current=null;$('card').hidden=true;$('empty').hidden=false;render()}function key(u){return kind()==='morph'?u.form:u.id}function text(u){return JSON.stringify(u)}function render(){let q=$('q').value.trim(),rows=units.filter(u=>!q||text(u).includes(q));$('list').innerHTML=rows.map(u=>`<div class="unit ${current&&key(current)===key(u)?'on':''}" data-key="${esc(key(u))}"><div class=id>${esc(key(u))}</div><div class=bor>${esc(kind()==='morph'?((u.lemma||'')+' · '+(u.glossa_conllu||'')):(kind()==='hm'?(u.reviewed||u.witness_a):((kind()==='adugo'||kind()==='boeero')?(u.reviewed||u.source):(kind()==='bakarudoge'||kind()==='bibliaoral'||kind()==='paulinho'||kind()==='oieigo'||['jonas','ageu','cantico'].includes(kind())?(u.reviewed||u.source):u.bororo)))).slice(0,180)}</div></div>`).join('');document.querySelectorAll('.unit').forEach(e=>e.onclick=()=>select(e.dataset.key))}async function select(k){current=units.find(u=>key(u)===k);$('empty').hidden=true;$('card').hidden=false;$('uid').textContent=key(current);let m=kind()==='morph';$('commentwrap').hidden=true;if(kind()==='oieigo'){let cr=await fetch('/api/comment');let cj=await cr.json();$('textcomment').value=cj.comment||'';$('commentwrap').hidden=false}$('normal').hidden=m;$('morphform').hidden=!m;if(m){$('docwrap').hidden=true;$('docptwrap').hidden=true;$('cf').textContent=current.form||'—';$('freq').textContent=current.frequency||0;$('cl').textContent=current.lemma||'—';$('cc').textContent=current.classe||'—';$('cg').textContent=current.glossa_conllu||'—';$('cp').textContent=current.classe_posse||'—';$('cpr').textContent=current.proclitico||'—';$('ms').value=current.segmentation||'';$('mm').value=current.morphemes||'';$('mg').value=current.gloss||'';$('mst').value=current.status||'';$('mn').value=current.note||''}else{$('docwrap').hidden=true;$('docptwrap').hidden=true;let h=kind()==='hm',d=(kind()==='adugo'||kind()==='boeero');if(h){$('l1').textContent='Testemunho A';$('l2').textContent='Texto revisado atual';$('a').textContent=current.witness_a;$('b').textContent=current.reviewed||'— ainda não estabelecido —';$('editlabel').textContent='Texto revisado';$('edit').value=current.reviewed||'';$('porwrap').hidden=true}else if(kind()==='bakarudoge'){$('l1').textContent='Bororo da fonte';$('l2').textContent='Tradução linear atual';$('a').textContent=current.source||'';$('b').textContent=current.linear_portuguese||'— ainda sem tradução linear —';$('editlabel').textContent='Bororo revisado';$('edit').value=current.reviewed||current.source||'';$('porwrap').hidden=false;$('pedit').value=current.linear_portuguese||'';$('porwrap').querySelector('.label').textContent='Tradução linear (editável)';$('docptwrap').hidden=!(current.documentary_translation||current.translation_candidate);$('docptlabel').textContent=current.documentary_translation?'Tradução portuguesa documental alinhada':'Trecho português documental candidato — alinhamento não confirmado';$('docpt').textContent=current.documentary_translation||current.translation_candidate||'';$('docwrap').hidden=false;$('snum').textContent=current.myth_number||'—';$('tnum').textContent=current.source_number||'—';$('ednote').textContent=current.title||'';$('notewrap').hidden=false}else if(['jonas','ageu','cantico'].includes(kind())){$('l1').textContent='Bororo da fonte';$('l2').textContent='Texto revisado atual';$('a').textContent=current.source||'';$('b').textContent=current.reviewed||'— ainda não revisado —';$('editlabel').textContent='Bororo revisado';$('edit').value=current.reviewed||current.source||'';$('porwrap').hidden=false;$('porwrap').querySelector('.label').textContent='Tradução portuguesa';$('pedit').value=current.portuguese||'';}else if(kind()==='bibliaoral'||kind()==='paulinho'||kind()==='oieigo'){$('l1').textContent='Bororo da fonte';$('l2').textContent='Tradução portuguesa atual';$('a').textContent=current.source||'';$('b').textContent=current.portuguese_reviewed||current.portuguese||'—';$('editlabel').textContent='Bororo revisado';$('edit').value=current.reviewed||current.source||'';$('porwrap').hidden=false;$('porwrap').querySelector('.label').textContent='Tradução portuguesa revisada';$('pedit').value=current.portuguese_reviewed||current.portuguese||'';$('docptwrap').hidden=false;$('docptlabel').textContent='Interlinear da fonte (segmentação + glosas)';$('docpt').textContent=[current.segmentation,current.gloss].filter(Boolean).join('\n');}else if(d){$('l1').textContent=kind()==='boeero'?'Fonte original':'Fonte reconstruída';$('l2').textContent='Texto revisado atual';$('a').textContent=current.source;$('b').textContent=current.reviewed||'— ainda não revisado —';$('editlabel').textContent='Bororo revisado';$('edit').value=current.reviewed||current.source;$('pedit').value=current.portuguese||'';$('porwrap').hidden=false;$('docwrap').hidden=kind()!=='boeero';if(kind()==='boeero'){$('snum').textContent=current.source_number||'—';$('tnum').textContent=current.translation_number||'—';$('ednote').textContent=current.editorial_note||'';$('notewrap').hidden=!current.editorial_note}}else{$('l1').textContent='Bororo publicado';$('l2').textContent='Português publicado';$('a').textContent=current.bororo;$('b').textContent=current.portuguese;$('editlabel').textContent='Bororo revisado';$('edit').value=current.bororo;$('pedit').value=current.portuguese;$('porwrap').hidden=false}}$('status').textContent='';render()}$('corpus').onchange=load;$('q').oninput=render;$('reset').onclick=()=>current&&select(key(current));$('save').onclick=async()=>{if(!current)return;let body=kind()==='morph'?{form:current.form,segmentation:$('ms').value,morphemes:$('mm').value,gloss:$('mg').value,status:$('mst').value,note:$('mn').value}:kind()==='hm'?{id:current.id,reviewed:$('edit').value}:kind()==='bakarudoge'?{id:current.id,reviewed:$('edit').value,linear_portuguese:$('pedit').value}:(['jonas','ageu','cantico'].includes(kind()))?{id:current.id,reviewed:$('edit').value,portuguese:$('pedit').value}:(kind()==='bibliaoral'||kind()==='paulinho'||kind()==='oieigo')?{id:current.id,reviewed:$('edit').value,portuguese_reviewed:$('pedit').value,comment:kind()==='oieigo'?$('textcomment').value:''}:(kind()==='adugo'||kind()==='boeero')?{id:current.id,reviewed:$('edit').value,portuguese:$('pedit').value}:{id:current.id,bororo:$('edit').value,portuguese:$('pedit').value};let r=await fetch('/api/save?corpus='+kind(),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}),x=await r.json();if(!r.ok){$('status').textContent='Erro: '+x.error;return}$('status').textContent='Revisão salva.';let k=x.key||x.id;await load();select(k)};$('build').onclick=async()=>{$('buildstatus').textContent='Validando…';let r=await fetch('/api/build',{method:'POST'}),x=await r.json();$('buildstatus').textContent=r.ok?'OK: '+x.output:'Erro: '+x.error};load()</script></body></html>'''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def js(self,o,status=200):
  d=json.dumps(o,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(d)));self.end_headers();self.wfile.write(d)
 def corpus(self):return parse_qs(urlparse(self.path).query).get('corpus',['coqueiro'])[0]
 def do_GET(self):
  p=urlparse(self.path).path
  if p=='/':
   d=PAGE.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(d)));self.end_headers();self.wfile.write(d);return
  if p=='/api/comment':
   self.js({'comment':OIEIGO_COMMENT.read_text(encoding='utf-8') if OIEIGO_COMMENT.exists() else ''});return
  if p=='/api/units':
   try:
    c=self.corpus();self.js(morph_rows() if c=='morph' else bakarudoge_units() if c=='bakarudoge' else bible_editor_units(c) if c in BIBLES else read_rows(c))
   except Exception as e:self.js({'error':str(e)},400)
   return
  self.send_error(404)
 def do_POST(self):
  p=urlparse(self.path).path
  if p=='/api/save':
   try:
    c=self.corpus();n=int(self.headers.get('Content-Length','0'));body=json.loads(self.rfile.read(n))
    if c=='morph':
     form=str(body.get('form','')).strip()
     if not form:raise ValueError('Forma vazia')
     rows=read_rows('morph');m=next((r for r in rows if r['form'].casefold()==form.casefold()),None)
     data={'form':form,**{f:str(body.get(f,'')).strip() for f in MF[1:]}}
     if m:m.update(data)
     else:rows.append(data)
     write_rows('morph',rows,MF);self.js({'ok':True,'key':form});return
    uid=str(body.get('id','')).strip()
    if c in BIBLES:
     if not any(r['id']==uid for r in bible_editor_units(c)):raise ValueError('ID bíblico não encontrado')
     save_bible(c,body);build_indexes();self.js({'ok':True,'id':uid,'rebuilt':True});return
    if c in ('bibliaoral','paulinho','oieigo'):
     rows=read_rows(c);uid=str(body.get('id','')).strip();m=[r for r in rows if r['id']==uid]
     if len(m)!=1:raise ValueError('ID estável não encontrado ou duplicado')
     m[0]['reviewed']=str(body.get('reviewed','')).strip();m[0]['portuguese_reviewed']=str(body.get('portuguese_reviewed','')).strip();write_rows(c,rows)
     if c=='oieigo':OIEIGO_COMMENT.write_text(str(body.get('comment','')).strip()+'\n',encoding='utf-8')
     self.js({'ok':True,'id':uid});return
    if c=='bakarudoge':
     if not any(r['id']==uid for r in bakarudoge_units()):raise ValueError('ID estável Bakarudoge não encontrado')
     save_bakarudoge_edit(body);self.js({'ok':True,'id':uid,'rebuilt':False});return
    rows=read_rows(c);m=[r for r in rows if r['id']==uid]
    if len(m)!=1:raise ValueError('ID estável não encontrado ou duplicado')
    if c=='hm':m[0]['reviewed']=str(body.get('reviewed','')).strip()
    elif c in ('adugo','boeero'):
     rev=str(body.get('reviewed','')).strip()
     if not rev:raise ValueError('Texto Bororo revisado não pode ficar vazio')
     m[0]['reviewed']=rev;m[0]['portuguese']=str(body.get('portuguese','')).strip()
    else:
     bor=str(body.get('bororo','')).strip()
     if not bor:raise ValueError('Texto Bororo não pode ficar vazio')
     m[0]['bororo']=bor;m[0]['portuguese']=str(body.get('portuguese','')).strip()
    write_rows(c,rows);build_indexes();self.js({'ok':True,'id':uid,'rebuilt':True})
   except Exception as e:self.js({'error':str(e)},400)
   return
  if p=='/api/build':
   try:
    cp=subprocess.run([sys.executable,str(BUILD)],cwd=ROOT,text=True,capture_output=True,check=True);self.js({'ok':True,'output':cp.stdout.strip()})
   except subprocess.CalledProcessError as e:self.js({'error':(e.stderr or e.stdout).strip()},400)
   return
  self.send_error(404)
def main():
 if not FILES['coqueiro'].exists():raise SystemExit('Arquivo TSV canônico do Coqueiro não encontrado')
 url=f'http://{HOST}:{PORT}';server=ThreadingHTTPServer((HOST,PORT),Handler);print('Editor do CorBo:',url);print('Ctrl-C para encerrar. As alterações permanecem locais até commit/push no Git.');threading.Timer(.6,lambda:webbrowser.open(url)).start()
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
