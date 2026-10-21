#!/usr/bin/env python3
"""Editor local de revisão gold do CorBo. Não altera o CoNLL-U."""
import csv, json, os, tempfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tokenizer_gold_review_100.tsv"
FIELDS = ["sent_id", "text", "tokens_conllu", "gold_tokens", "reviewed"]
PAGE = """<!doctype html><html lang="pt"><meta charset="utf-8"><title>CorBo · Revisão</title>
<style>body{font:16px system-ui;max-width:900px;margin:40px auto;padding:20px;color:#193047;background:#f5f7fa}main{background:white;padding:28px;border-radius:12px}pre{white-space:pre-wrap;background:#eef2f7;padding:15px}textarea{width:98%;height:90px;font:17px system-ui}button{padding:10px;margin:6px;background:#174b78;color:white;border:0;border-radius:6px;cursor:pointer}</style>
<main><h1>CorBo · Revisão de tokenização UD</h1><p>Revisão local; o corpus original não é alterado.</p><p id="progress"></p><h3>Texto original</h3><pre id="text"></pre><h3>Tokens CoNLL-U (hipótese)</h3><pre id="tokens"></pre><h3>Tokens gold (separados por |)</h3><textarea id="gold"></textarea><br>
<button onclick="save('approved')">Aprovar</button><button onclick="save('corrected')">Corrigir</button><button onclick="move(-1)">Anterior</button><button onclick="move(1)">Próxima</button><button onclick="pending()">Próxima pendente</button><p id="msg"></p></main>
<script>
let rows=[],pos=0;
function render(){let r=rows[pos];if(!r)return;document.getElementById('progress').textContent=(pos+1)+' / '+rows.length+' · Revisadas: '+rows.filter(x=>['approved','corrected'].includes(x.reviewed)).length+' · '+r.sent_id;document.getElementById('text').textContent=r.text;document.getElementById('tokens').textContent=r.tokens_conllu;document.getElementById('gold').value=r.gold_tokens;document.getElementById('msg').textContent=''}
function move(n){pos=Math.max(0,Math.min(rows.length-1,pos+n));render()}
function pending(){let i=rows.findIndex((r,j)=>j>pos&&!r.reviewed);if(i<0)i=rows.findIndex(r=>!r.reviewed);if(i>=0)pos=i;render()}
async function save(state){let gold=state==='approved'?rows[pos].tokens_conllu:document.getElementById('gold').value.trim();if(!gold||gold.split('|').some(x=>!x.trim())){document.getElementById('msg').textContent='Tokens inválidos';return}let response=await fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:pos,gold_tokens:gold,reviewed:state})});let result=await response.json();if(!response.ok){document.getElementById('msg').textContent=result.error;return}rows[pos]=result.row;if(pos<rows.length-1)pos++;render()}
fetch('/rows').then(r=>r.json()).then(x=>{rows=x;render()}).catch(e=>document.getElementById('msg').textContent=e.message);
</script>"""
def read_rows():
    with DATA.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f,delimiter="\t")
        if reader.fieldnames!=FIELDS: raise ValueError("Cabeçalho TSV inesperado")
        return list(reader)
def write_rows(rows):
    fd,path=tempfile.mkstemp(dir=ROOT,prefix=".gold_",suffix=".tsv")
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t",lineterminator="\n")
            writer.writeheader();writer.writerows(rows)
        os.replace(path,DATA)
    finally:
        if os.path.exists(path):os.unlink(path)
class Handler(BaseHTTPRequestHandler):
    def respond(self,code,obj,typ="application/json"):
        data=(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False)).encode("utf-8")
        self.send_response(code);self.send_header("Content-Type",typ+"; charset=utf-8");self.send_header("Content-Length",str(len(data)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=="/":self.respond(200,PAGE,"text/html")
        elif self.path=="/rows":self.respond(200,read_rows())
        else:self.respond(404,{"error":"Não encontrado"})
    def do_POST(self):
        if self.path!="/save":return self.respond(404,{"error":"Não encontrado"})
        try:
            size=int(self.headers.get("Content-Length","0"))
            if size<1 or size>100000:raise ValueError("Tamanho inválido")
            req=json.loads(self.rfile.read(size));rows=read_rows()
            idx=req["index"];state=req["reviewed"];gold=req["gold_tokens"].strip()
            if type(idx)!=int or not 0<=idx<len(rows):raise ValueError("Índice inválido")
            if state not in ("approved","corrected"):raise ValueError("Estado inválido")
            if not gold or any(not x.strip() for x in gold.split("|")):raise ValueError("Tokens inválidos")
            if state=="approved" and gold!=rows[idx]["tokens_conllu"]:raise ValueError("Aprovação inconsistente")
            rows[idx]["gold_tokens"]=gold;rows[idx]["reviewed"]=state
            write_rows(rows);self.respond(200,{"row":rows[idx]})
        except (ValueError,KeyError,TypeError) as e:self.respond(400,{"error":str(e)})
if __name__=="__main__":
    if not DATA.exists():raise SystemExit("Arquivo ausente: "+str(DATA))
    print("Editor: http://127.0.0.1:8777",flush=True)
    ThreadingHTTPServer(("127.0.0.1",8777),Handler).serve_forever()
