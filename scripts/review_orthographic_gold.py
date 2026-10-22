#!/usr/bin/env python3
"""Editor local da amostra de tokenização CorBo.

Execute: python3 scripts/review_orthographic_gold.py
Acesse: http://127.0.0.1:8770
Somente o TSV de revisão é modificado; nunca o corpus.
"""
import csv,json
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"tokenizer_orthographic_gold_review.tsv"
COLUMNS=["sent_id","text","predicted_tokens","corrected_tokens","review_status","notes"]
STATUSES={"approved","corrected","source_error"}

def load():
    with FILE.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f,delimiter="\t"))

def save(rows):
    temp=FILE.with_suffix(".tmp")
    with temp.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS,delimiter="\t",extrasaction="ignore")
        w.writeheader();w.writerows(rows)
    temp.replace(FILE)

def valid_tokens(text,value):
    parts=[p.strip() for p in value.split("|")]
    return bool(parts) and all(parts) and "".join(parts)=="".join(text.split())

PAGE=r"""<!doctype html><html lang="pt"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CorBo · Revisão do tokenizador</title>
<style>body{font:17px system-ui;max-width:850px;margin:2em auto;padding:0 1em;color:#1b2736}
h1{font-size:1.5em}#text{font-size:1.3em;background:#f2f5f8;padding:1em;line-height:1.6}
textarea{box-sizing:border-box;width:100%;min-height:90px;font:inherit;padding:.6em}
button{font:inherit;padding:.55em;margin:.3em .3em .3em 0;cursor:pointer}
label{display:block;margin-top:1em}#notes{min-height:60px}
#message{color:#a02727;min-height:1.5em}</style>
<h1>CorBo · Revisão ortográfica</h1><p id="progress"></p>
<p id="text"></p>
<label>Tokenização (separar com |)<textarea id="tokens"></textarea></label>
<label>Observações<textarea id="notes"></textarea></label>
<p><button id="prev">← Anterior</button><button id="approve">Aprovar</button>
<button id="correct">Salvar correção</button><button id="source">Erro no texto original</button>
<button id="next">Próxima →</button></p>
<p id="message" role="status"></p>
<p><small>Erro no texto original exclui a frase da avaliação gold. O corpus não é alterado.</small></p>
<script>
let rows=[],idx=0;
const el=id=>document.getElementById(id);
async function init(){
 const response=await fetch('/api/rows');rows=await response.json();
 if(!rows.length){el('message').textContent='Arquivo vazio.';return;}
 const pending=rows.findIndex(r=>!['approved','corrected','source_error'].includes(r.review_status));
 idx=pending<0?0:pending;render();
}
function render(){
 const r=rows[idx];if(!r)return;
 const done=rows.filter(r=>['approved','corrected','source_error'].includes(r.review_status)).length;
 el('progress').textContent=(idx+1)+'/'+rows.length+' · '+done+' revisadas · '+r.sent_id+' · '+(r.review_status||'pendente');
 el('text').textContent=r.text;
 el('tokens').value=r.corrected_tokens||r.predicted_tokens;
 el('notes').value=r.notes||'';
 el('message').textContent='';
}
async function submit(status){
 const r=rows[idx];
 const payload={sent_id:r.sent_id,corrected_tokens:el('tokens').value.trim(),
   review_status:status,notes:el('notes').value};
 const response=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 const result=await response.json();
 if(!response.ok){el('message').textContent=result.error||'Erro';return;}
 Object.assign(r,payload);if(idx<rows.length-1)idx++;render();
}
el('prev').onclick=()=>{if(idx>0)idx--;render()};
el('next').onclick=()=>{if(idx<rows.length-1)idx++;render()};
el('approve').onclick=()=>submit('approved');
el('correct').onclick=()=>submit('corrected');
el('source').onclick=()=>submit('source_error');
init().catch(e=>el('message').textContent=e.message);
</script></html>"""

class Handler(BaseHTTPRequestHandler):
    def send(self,status,body,content_type):
        data=body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Cache-Control","no-store")
        self.end_headers();self.wfile.write(data)
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=="/":
            return self.send(200,PAGE,"text/html; charset=utf-8")
        if path=="/api/rows":
            return self.send(200,json.dumps(load(),ensure_ascii=False),"application/json; charset=utf-8")
        self.send(404,"Not found","text/plain; charset=utf-8")
    def do_POST(self):
        if urlsplit(self.path).path!="/api/save":
            return self.send(404,"{}","application/json")
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length>100000 or length<1:raise ValueError("Tamanho inválido")
            data=json.loads(self.rfile.read(length))
            sid=data.get("sent_id")
            status=data.get("review_status")
            tokens=data.get("corrected_tokens","")
            notes=data.get("notes","")
            if not all(isinstance(x,str) for x in (sid,status,tokens,notes)):
                raise ValueError("Campos inválidos")
            if status not in STATUSES:raise ValueError("Estado inválido")
            rows=load()
            row=next((r for r in rows if r["sent_id"]==sid),None)
            if row is None:raise ValueError("ID desconhecido")
            if status!="source_error" and not valid_tokens(row["text"],tokens):
                raise ValueError("Os tokens devem reconstruir exatamente o texto (ignorando espaços)")
            if status=="approved" and tokens!=row["predicted_tokens"]:
                raise ValueError("Use Salvar correção para alterar a proposta")
            if status=="source_error" and not notes.strip():
                raise ValueError("Descreva o erro do texto original nas observações")
            row["corrected_tokens"]=tokens
            row["review_status"]=status
            row["notes"]=notes
            save(rows)
            self.send(200,'{"ok":true}',"application/json")
        except (ValueError,KeyError,json.JSONDecodeError) as e:
            self.send(400,json.dumps({"error":str(e)},ensure_ascii=False),"application/json; charset=utf-8")

if __name__=="__main__":
    if not FILE.exists():raise SystemExit("Execute primeiro prepare_orthographic_gold.py")
    print("Editor: http://127.0.0.1:8770/")
    HTTPServer(("127.0.0.1",8770),Handler).serve_forever()
