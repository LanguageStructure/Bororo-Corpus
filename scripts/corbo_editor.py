#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Editor local do CorBo. Acesso somente em 127.0.0.1."""
from __future__ import annotations
import csv,json,subprocess,sys,threading,webbrowser
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from build_corpus_indexes import conllu_relations,CONLLU,main as build_indexes
ROOT=Path(__file__).resolve().parents[1]
FILES={'coqueiro':ROOT/'CorBo_vNext/texts/coqueiro/coqueiro_parallel.tsv','hm':ROOT/'CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv','adugo':ROOT/'CorBo_vNext/texts/adugo-biri/adugo_biri_parallel.tsv','morph':ROOT/'CorBo_vNext/annotations/morphology.tsv'}
BUILD=ROOT/'scripts/build_corpus_indexes.py'; HOST='127.0.0.1'; PORT=8765
MF=['form','segmentation','morphemes','gloss','status','note']
def read_rows(c):
 with FILES[c].open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write_rows(c,rows,fields=None):
 p=FILES[c];tmp=p.with_suffix('.tsv.tmp');fields=fields or list(rows[0].keys())
 with tmp.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 tmp.replace(p)
def vals(a):return ', '.join(x['value'] for x in (a or []))
def morph_rows():
 ed={r['form'].casefold():r for r in read_rows('morph')}
 out=[]
 for r in conllu_relations(CONLLU):
  e=ed.pop(r['form'].casefold(),{})
  out.append({'form':r['form'],'frequency':r['frequency'],'lemma':vals(r['lemmas']),'classe':vals(r['pos_detalhada']) or vals(r['upos']),'glossa_conllu':vals(r['glossas']),'classe_posse':vals(r['classes_posse']),'proclitico':vals(r['procliticos']),'segmentation':e.get('segmentation',''),'morphemes':e.get('morphemes',''),'gloss':e.get('gloss',''),'status':e.get('status',''),'note':e.get('note',''),'editorial':bool(e)})
 for e in ed.values():out.append({'form':e['form'],'frequency':0,'lemma':'','classe':'','glossa_conllu':'','classe_posse':'','proclitico':'','segmentation':e.get('segmentation',''),'morphemes':e.get('morphemes',''),'gloss':e.get('gloss',''),'status':e.get('status',''),'note':e.get('note',''),'editorial':True})
 return out
PAGE=r'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Editor do CorBo</title><style>:root{font-family:system-ui,sans-serif;color:#202124;background:#f6f4ef}*{box-sizing:border-box}body{margin:0}header{padding:18px 26px;background:#fff;border-bottom:1px solid #ddd;display:flex;gap:24px;align-items:center}h1{margin:0;font:25px Georgia,serif}select,input,textarea{font:inherit;border:1px solid #bbb;border-radius:6px;padding:10px;background:#fff}select{min-width:190px}.grid{display:grid;grid-template-columns:minmax(320px,32%) 1fr;height:calc(100vh - 75px)}aside{padding:18px;border-right:1px solid #ddd;overflow:auto;background:#fff}aside input{width:100%}main{padding:26px;overflow:auto}.unit{padding:9px 6px;border-bottom:1px solid #eee;cursor:pointer}.unit:hover,.unit.on{background:#f0eee7}.id{font:12px ui-monospace,monospace;color:#666}.bor{font-family:Georgia,serif}.card{max-width:1050px;background:#fff;border:1px solid #ddd;border-radius:8px;padding:22px}.cols{display:grid;grid-template-columns:1fr 1fr;gap:18px}.published{padding:12px;background:#f7f7f7;border-radius:6px;white-space:pre-wrap;min-height:48px}.label{font-weight:650;margin:15px 0 6px}textarea,input.field,select.field{width:100%}textarea{min-height:100px}.wide{grid-column:1/-1}button{padding:10px 14px;border:0;border-radius:6px;cursor:pointer;font-weight:650}.primary{background:#222;color:#fff}.secondary{background:#e7e5df;margin-left:8px}.actions{margin-top:20px}.status{margin-left:12px;color:#555}.notice{padding:10px 12px;background:#fff7d6;border-radius:6px;margin:12px 0}.source{background:#edf3ee;padding:14px;border-radius:7px;margin-bottom:18px}@media(max-width:800px){.grid{display:block;height:auto}.cols{grid-template-columns:1fr}aside{max-height:35vh}}</style></head><body><header><h1>Editor do CorBo</h1><select id="corpus"><option value="coqueiro">Coqueiro</option><option value="hm">História Mítica</option><option value="adugo">Adugo Biri</option><option value="morph">Morfologia</option></select><span class="id">local · 127.0.0.1</span></header><div class="grid"><aside><input id="q" placeholder="Buscar (diferencia maiúsculas/minúsculas)"><div id="list"></div></aside><main><div id="empty">Selecione uma entrada.</div><div id="card" class="card" hidden><div class="id" id="uid"></div><div id="normal"><div class="cols"><section><div class="label" id="l1"></div><div class="published bor" id="a"></div></section><section><div class="label" id="l2"></div><div class="published" id="b"></div></section><section class="wide"><div class="label" id="editlabel"></div><textarea id="edit"></textarea></section><section class="wide" id="porwrap"><div class="label">Português revisado</div><textarea id="pedit"></textarea></section></div></div><div id="morphform" hidden><div class="notice">Os dados abaixo vêm do CoNLL-U e permanecem preservados. Sua revisão é registrada separadamente como camada editorial.</div><div class="source"><div class="cols"><div><b>Forma:</b> <span id="cf"></span></div><div><b>Frequência:</b> <span id="freq"></span></div><div><b>Lema:</b> <span id="cl"></span></div><div><b>Classe gramatical:</b> <span id="cc"></span></div><div><b>Glossa:</b> <span id="cg"></span></div><div><b>Classe de posse:</b> <span id="cp"></span></div><div><b>Proclítico:</b> <span id="cpr"></span></div><div><b>Fonte:</b> CoNLL-U</div></div></div><h2>Revisão editorial</h2><div class="cols"><section><div class="label">Segmentação</div><input class="field" id="ms"></section><section><div class="label">Morfemas (separados por |)</div><input class="field" id="mm"></section><section><div class="label">Glosas editoriais (separadas por |)</div><input class="field" id="mg"></section><section><div class="label">Estado da análise</div><select class="field" id="mst"><option value="">Sem revisão</option><option value="confirmed">Confirmada</option><option value="partial">Parcial</option><option value="provisional">Provisória</option></select></section><section class="wide"><div class="label">Nota</div><textarea id="mn"></textarea></section></div></div><div class="actions"><button class="primary" id="save">Salvar revisão</button><button class="secondary" id="reset">Restaurar campos</button><span class="status" id="status"></span></div><div class="actions"><button class="secondary" id="build">Validar e regenerar dados</button><span class="status" id="buildstatus"></span></div></div></main></div><script>let units=[],current=null;const $=x=>document.getElementById(x),kind=()=>$('corpus').value;function esc(s){let d=document.createElement('div');d.textContent=s||'';return d.innerHTML}async function load(){let r=await fetch('/api/units?corpus='+kind()),x=await r.json();if(!r.ok){$('list').innerHTML='<div class=notice>'+esc(x.error)+'</div>';return}units=x;current=null;$('card').hidden=true;$('empty').hidden=false;render()}function key(u){return kind()==='morph'?u.form:u.id}function text(u){return JSON.stringify(u)}function render(){let q=$('q').value.trim(),rows=units.filter(u=>!q||text(u).includes(q));$('list').innerHTML=rows.map(u=>`<div class="unit ${current&&key(current)===key(u)?'on':''}" data-key="${esc(key(u))}"><div class=id>${esc(key(u))}</div><div class=bor>${esc(kind()==='morph'?((u.lemma||'')+' · '+(u.glossa_conllu||'')):(kind()==='hm'?(u.reviewed||u.witness_a):(kind()==='adugo'?(u.reviewed||u.source):u.bororo))).slice(0,180)}</div></div>`).join('');document.querySelectorAll('.unit').forEach(e=>e.onclick=()=>select(e.dataset.key))}function select(k){current=units.find(u=>key(u)===k);$('empty').hidden=true;$('card').hidden=false;$('uid').textContent=key(current);let m=kind()==='morph';$('normal').hidden=m;$('morphform').hidden=!m;if(m){$('cf').textContent=current.form||'—';$('freq').textContent=current.frequency||0;$('cl').textContent=current.lemma||'—';$('cc').textContent=current.classe||'—';$('cg').textContent=current.glossa_conllu||'—';$('cp').textContent=current.classe_posse||'—';$('cpr').textContent=current.proclitico||'—';$('ms').value=current.segmentation||'';$('mm').value=current.morphemes||'';$('mg').value=current.gloss||'';$('mst').value=current.status||'';$('mn').value=current.note||''}else{let h=kind()==='hm',d=kind()==='adugo';if(h){$('l1').textContent='Testemunho A';$('l2').textContent='Texto revisado atual';$('a').textContent=current.witness_a;$('b').textContent=current.reviewed||'— ainda não estabelecido —';$('editlabel').textContent='Texto revisado';$('edit').value=current.reviewed||'';$('porwrap').hidden=true}else if(d){$('l1').textContent='Fonte reconstruída';$('l2').textContent='Texto revisado atual';$('a').textContent=current.source;$('b').textContent=current.reviewed||'— ainda não revisado —';$('editlabel').textContent='Bororo revisado';$('edit').value=current.reviewed||current.source;$('pedit').value=current.portuguese||'';$('porwrap').hidden=false}else{$('l1').textContent='Bororo publicado';$('l2').textContent='Português publicado';$('a').textContent=current.bororo;$('b').textContent=current.portuguese;$('editlabel').textContent='Bororo revisado';$('edit').value=current.bororo;$('pedit').value=current.portuguese;$('porwrap').hidden=false}}$('status').textContent='';render()}$('corpus').onchange=load;$('q').oninput=render;$('reset').onclick=()=>current&&select(key(current));$('save').onclick=async()=>{if(!current)return;let body=kind()==='morph'?{form:current.form,segmentation:$('ms').value,morphemes:$('mm').value,gloss:$('mg').value,status:$('mst').value,note:$('mn').value}:kind()==='hm'?{id:current.id,reviewed:$('edit').value}:kind()==='adugo'?{id:current.id,reviewed:$('edit').value,portuguese:$('pedit').value}:{id:current.id,bororo:$('edit').value,portuguese:$('pedit').value};let r=await fetch('/api/save?corpus='+kind(),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}),x=await r.json();if(!r.ok){$('status').textContent='Erro: '+x.error;return}$('status').textContent='Revisão salva.';let k=x.key||x.id;await load();select(k)};$('build').onclick=async()=>{$('buildstatus').textContent='Validando…';let r=await fetch('/api/build',{method:'POST'}),x=await r.json();$('buildstatus').textContent=r.ok?'OK: '+x.output:'Erro: '+x.error};load()</script></body></html>'''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def js(self,o,status=200):
  d=json.dumps(o,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(d)));self.end_headers();self.wfile.write(d)
 def corpus(self):return parse_qs(urlparse(self.path).query).get('corpus',['coqueiro'])[0]
 def do_GET(self):
  p=urlparse(self.path).path
  if p=='/':
   d=PAGE.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(d)));self.end_headers();self.wfile.write(d);return
  if p=='/api/units':
   try:
    c=self.corpus();self.js(morph_rows() if c=='morph' else read_rows(c))
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
    rows=read_rows(c);uid=str(body.get('id','')).strip();m=[r for r in rows if r['id']==uid]
    if len(m)!=1:raise ValueError('ID estável não encontrado ou duplicado')
    if c=='hm':m[0]['reviewed']=str(body.get('reviewed','')).strip()
    elif c=='adugo':
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
