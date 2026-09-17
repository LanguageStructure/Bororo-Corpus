#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Editor local dos textos bíblicos do CorBo. Somente 127.0.0.1."""
import csv,json,re,threading,webbrowser
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
ROOT=Path(__file__).resolve().parents[1];HOST='127.0.0.1';PORT=8766
BOOKS={'jonas':('Jonas','CorBo/Corpus_Files/bíblia/jonas_2-orthophon.txt','CorBo_vNext/texts/biblia/jonas_review.tsv','JON'),'ageu':('Ageu','CorBo/Corpus_Files/bíblia/ageu_2-orthophon.txt','CorBo_vNext/texts/biblia/ageu_review.tsv','AGE'),'cantico':('Cântico dos Cânticos','CorBo/Corpus_Files/bíblia/cantico_dos_canticos_2-orthophon.txt','CorBo_vNext/texts/biblia/cantico_review.tsv','CAN')}
def rows(book):
 title,src,rev,prefix=BOOKS[book];rp=ROOT/rev;ed={}
 if rp.exists():
  with rp.open(encoding='utf-8',newline='') as f:ed={r['id']:r for r in csv.DictReader(f,delimiter='\t')}
 paras=[x.strip() for x in re.split(r'\n\s*\n',(ROOT/src).read_text(encoding='utf-8')) if x.strip()];out=[]
 for i,s in enumerate(paras,1):
  uid=f'BOR-CORBO-BIB-{prefix}-{i:04d}';e=ed.get(uid,{});out.append({'id':uid,'source':s,'reviewed':e.get('reviewed',''),'portuguese':e.get('portuguese','')})
 return out
def save(book,body):
 _,_,rev,_=BOOKS[book];rp=ROOT/rev;rs=rows(book);uid=body['id'];m=next(x for x in rs if x['id']==uid);m['reviewed']=str(body.get('reviewed','')).strip();m['portuguese']=str(body.get('portuguese','')).strip();rp.parent.mkdir(parents=True,exist_ok=True);tmp=rp.with_suffix('.tmp')
 with tmp.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['id','reviewed','portuguese'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows({'id':x['id'],'reviewed':x['reviewed'],'portuguese':x['portuguese']} for x in rs if x['reviewed'] or x['portuguese'])
 tmp.replace(rp)
PAGE='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Editor bíblico · CorBo</title><style>body{margin:0;font:15px system-ui;background:#f6f3ec;color:#17211c}header{padding:18px 24px;background:#173c2d;color:white}select,input,textarea{font:inherit;padding:9px}.grid{display:grid;grid-template-columns:34% 1fr;height:calc(100vh - 66px)}aside{background:white;border-right:1px solid #ddd;padding:16px;overflow:auto}aside input{width:100%;box-sizing:border-box}.u{padding:9px;border-bottom:1px solid #eee;cursor:pointer}.u:hover{background:#eee}main{padding:24px;overflow:auto}.card{background:white;padding:22px;border:1px solid #ddd;border-radius:8px}.src{font:18px/1.6 Georgia,serif;background:#f4f4f1;padding:14px}textarea{width:100%;box-sizing:border-box;min-height:130px}button{padding:10px 14px;margin-top:14px}.id{font:12px monospace;color:#68716c}</style></head><body><header><b>Editor do CorBo · Textos bíblicos</b> &nbsp; <select id=b><option value=jonas>Jonas</option><option value=ageu>Ageu</option><option value=cantico>Cântico dos Cânticos</option></select> &nbsp; <span class=id>local · 127.0.0.1:8766</span></header><div class=grid><aside><input id=q placeholder=Buscar><div id=list></div></aside><main><div id=card class=card hidden><div id=id class=id></div><h3>Fonte preservada</h3><div id=src class=src></div><h3>Texto Bororo revisado</h3><textarea id=rev></textarea><h3>Tradução portuguesa</h3><textarea id=pt></textarea><button id=save>Salvar revisão</button> <span id=status></span></div></main></div><script>let data=[],cur=null,$=x=>document.getElementById(x),esc=s=>{let d=document.createElement('div');d.textContent=s||'';return d.innerHTML};async function load(){data=await(await fetch('/api/units?book='+b.value)).json();cur=null;card.hidden=true;render()}function render(){let z=q.value.toLowerCase();list.innerHTML=data.filter(x=>!z||JSON.stringify(x).toLowerCase().includes(z)).map(x=>`<div class=u data-id="${x.id}"><div class=id>${x.id}</div>${esc((x.reviewed||x.source).slice(0,130))}</div>`).join('');document.querySelectorAll('.u').forEach(x=>x.onclick=()=>sel(x.dataset.id))}function sel(id0){cur=data.find(x=>x.id===id0);card.hidden=false;id.textContent=cur.id;src.textContent=cur.source;rev.value=cur.reviewed||'';pt.value=cur.portuguese||'';status.textContent=''}b.onchange=load;q.oninput=render;save.onclick=async()=>{let r=await fetch('/api/save?book='+b.value,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:cur.id,reviewed:rev.value,portuguese:pt.value})});let x=await r.json();status.textContent=r.ok?'Revisão salva.':'Erro: '+x.error;await load();sel(x.id||cur.id)};load()</script></body></html>'''
class H(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def js(self,x,s=200):
  d=json.dumps(x,ensure_ascii=False).encode();self.send_response(s);self.send_header('Content-Type','application/json; charset=utf-8');self.end_headers();self.wfile.write(d)
 def book(self):return parse_qs(urlparse(self.path).query).get('book',['jonas'])[0]
 def do_GET(self):
  if urlparse(self.path).path=='/':d=PAGE.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(d)
  elif urlparse(self.path).path=='/api/units':self.js(rows(self.book()))
  else:self.send_error(404)
 def do_POST(self):
  try:
   n=int(self.headers.get('Content-Length',0));body=json.loads(self.rfile.read(n));save(self.book(),body);self.js({'ok':True,'id':body['id']})
  except Exception as e:self.js({'error':str(e)},400)
def main():
 u=f'http://{HOST}:{PORT}';s=ThreadingHTTPServer((HOST,PORT),H);print('Editor bíblico do CorBo:',u);threading.Timer(.5,lambda:webbrowser.open(u)).start()
 try:s.serve_forever()
 except KeyboardInterrupt:pass
if __name__=='__main__':main()
