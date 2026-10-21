#!/usr/bin/env python3
"""Revisão morfológica separada dos tokens UD; não modifica CoNLL-U."""
import csv,json,os,tempfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler,HTTPServer
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"tokenizer_gold_review_100.tsv"
OUT=ROOT/"tokenizer_morph_review_100.tsv"
FIELDS=["index","sent_id","text","tokens_conllu","morph_segments","reviewed"]
def read_source():
    with SOURCE.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def read_reviews():
    if not OUT.exists():return {}
    with OUT.open(encoding="utf-8-sig",newline="") as f:
        return {int(x["index"]):x for x in csv.DictReader(f,delimiter="\t")}
def write_reviews(rows):
    fd,tmp=tempfile.mkstemp(dir=ROOT,prefix=".morph_",suffix=".tsv")
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t")
            w.writeheader();w.writerows(rows[k] for k in sorted(rows))
        os.replace(tmp,OUT)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
HTML="""<!doctype html><html lang="pt"><meta charset="utf-8"><title>CorBo — Morfologia</title><style>body{font:17px system-ui;max-width:850px;margin:35px auto;padding:15px}pre{white-space:pre-wrap;background:#eee;padding:15px}textarea{width:98%;height:100px;font:18px system-ui}button{padding:10px;margin:8px}</style><h1>CorBo · Segmentação morfológica</h1><p>Camada independente dos tokens UD. Separe morfemas com |. O arquivo CoNLL-U não será alterado.</p><p id="progress"></p><h3>Texto</h3><pre id="text"></pre><h3>Tokens UD (referência)</h3><pre id="ud"></pre><h3>Morfemas revisados</h3><textarea id="morph"></textarea><br><button onclick="save()">Salvar revisão</button><button onclick="move(-1)">Anterior</button><button onclick="move(1)">Próxima</button><button onclick="pending()">Próxima pendente</button><p id="msg"></p><script>
let rows=[],i=0;
function render(){let r=rows[i];document.getElementById('progress').textContent=(i+1)+' / '+rows.length+' · revisadas '+rows.filter(x=>x.reviewed).length+' · '+r.sent_id;document.getElementById('text').textContent=r.text;document.getElementById('ud').textContent=r.tokens_conllu;document.getElementById('morph').value=r.morph_segments||'';document.getElementById('msg').textContent=''}
function move(n){i=Math.max(0,Math.min(rows.length-1,i+n));render()}
function pending(){let n=rows.findIndex((r,j)=>j>i&&!r.reviewed);if(n<0)n=rows.findIndex(r=>!r.reviewed);if(n>=0)i=n;render()}
async function save(){let v=document.getElementById('morph').value.trim();if(!v||v.split('|').some(x=>!x.trim())){document.getElementById('msg').textContent='Preencha morfemas separados por |';return}let response=await fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:i,morph_segments:v})});let data=await response.json();if(!response.ok){document.getElementById('msg').textContent=data.error;return}rows[i].morph_segments=v;rows[i].reviewed='yes';if(i<rows.length-1)i++;render()}
fetch('/rows').then(r=>r.json()).then(x=>{rows=x;render()});
</script></html>"""
class Handler(BaseHTTPRequestHandler):
    def send(self,status,obj,kind="application/json"):
        body=(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False)).encode()
        self.send_response(status);self.send_header("Content-Type",kind+"; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=="/":return self.send(200,HTML,"text/html")
        if self.path=="/rows":
            src=read_source();rev=read_reviews()
            return self.send(200,[dict(row,**{"morph_segments":rev.get(i,{}).get("morph_segments",""),"reviewed":rev.get(i,{}).get("reviewed","")}) for i,row in enumerate(src)])
        self.send(404,{"error":"Não encontrado"})
    def do_POST(self):
        if self.path!="/save":return self.send(404,{"error":"Não encontrado"})
        try:
            n=int(self.headers.get("Content-Length","0"))
            if not 0<n<100000:raise ValueError("Tamanho inválido")
            req=json.loads(self.rfile.read(n));idx=req["index"];value=req["morph_segments"].strip()
            src=read_source()
            if type(idx)!=int or not 0<=idx<len(src):raise ValueError("Índice inválido")
            if not value or any(not x.strip() for x in value.split("|")):raise ValueError("Segmentação inválida")
            rev=read_reviews()
            rev[idx]={"index":str(idx),"sent_id":src[idx]["sent_id"],"text":src[idx]["text"],"tokens_conllu":src[idx]["tokens_conllu"],"morph_segments":value,"reviewed":"yes"}
            write_reviews(rev);self.send(200,{"ok":True})
        except (ValueError,KeyError,TypeError) as e:self.send(400,{"error":str(e)})
if __name__=="__main__":
    if not SOURCE.exists():raise SystemExit("Arquivo ausente: "+str(SOURCE))
    print("Editor morfológico: http://127.0.0.1:8778/",flush=True)
    HTTPServer(("127.0.0.1",8778),Handler).serve_forever()
