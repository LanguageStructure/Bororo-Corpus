#!/usr/bin/env python3
"""Local-only editor for the canonical CorBo Coqueiro TSV.

Runs on 127.0.0.1 and never exposes an editing endpoint publicly.
Uses only the Python standard library.
"""
from __future__ import annotations

import csv
import html
import json
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TSV = ROOT / "CorBo_vNext" / "texts" / "coqueiro" / "coqueiro_parallel.tsv"
BUILD = ROOT / "scripts" / "build_corpus_indexes.py"
HOST = "127.0.0.1"
PORT = 8765
HEADER = ["id", "bororo", "portuguese"]


def read_units():
    with TSV.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        if r.fieldnames != HEADER:
            raise RuntimeError("Unexpected canonical TSV header")
        return list(r)


def write_units(units):
    tmp = TSV.with_suffix(".tsv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(units)
    tmp.replace(TSV)


PAGE = r'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CorBo Editor local</title><style>
:root{font-family:system-ui,-apple-system,sans-serif;color:#202124;background:#f6f4ef}*{box-sizing:border-box}body{margin:0}header{padding:20px 28px;background:#fff;border-bottom:1px solid #ddd}h1{margin:0;font-family:Georgia,serif;font-size:25px}.sub{color:#666;margin-top:5px}.grid{display:grid;grid-template-columns:minmax(280px,34%) 1fr;height:calc(100vh - 91px)}aside{padding:18px;border-right:1px solid #ddd;overflow:auto;background:#fff}main{padding:28px;overflow:auto}input,textarea{width:100%;font:inherit;border:1px solid #bbb;border-radius:6px;padding:10px;background:#fff}textarea{min-height:155px;line-height:1.45}.unit{padding:9px 6px;border-bottom:1px solid #eee;cursor:pointer}.unit:hover,.unit.on{background:#f0eee7}.id{font:12px ui-monospace,monospace;color:#666}.bor{font-family:Georgia,serif;margin-top:3px}.card{max-width:900px;background:#fff;border:1px solid #ddd;border-radius:8px;padding:22px}.cols{display:grid;grid-template-columns:1fr 1fr;gap:20px}.published{padding:12px;background:#f7f7f7;border-radius:6px;white-space:pre-wrap;min-height:80px}.label{font-weight:650;margin:17px 0 7px}button{padding:10px 14px;border:0;border-radius:6px;cursor:pointer;font-weight:650}button.primary{background:#222;color:#fff}button.secondary{background:#e7e5df;margin-left:8px}.status{margin-left:12px;color:#555}.actions{margin-top:20px}.publish{margin-top:28px;padding-top:20px;border-top:1px solid #ddd}@media(max-width:800px){.grid{display:block;height:auto}.cols{grid-template-columns:1fr}aside{max-height:38vh;border-right:0;border-bottom:1px solid #ddd}}
</style></head><body><header><h1>CorBo Editor</h1><div class="sub">Editor local · arquivo canônico Coqueiro · 127.0.0.1</div></header><div class="grid"><aside><input id="q" placeholder="Buscar ID, Bororo ou português"><div id="list"></div></aside><main><div id="empty">Selecione uma unidade.</div><div id="card" class="card" hidden><div class="id" id="uid"></div><div class="cols"><section><div class="label">Bororo publicado</div><div class="published bor" id="bp"></div><div class="label">Bororo revisado</div><textarea id="be"></textarea></section><section><div class="label">Português publicado</div><div class="published" id="pp"></div><div class="label">Português revisado</div><textarea id="pe"></textarea></section></div><div class="actions"><button class="primary" id="save">Salvar correção</button><button class="secondary" id="reset">Restaurar campos</button><span class="status" id="status"></span></div><div class="publish"><button class="secondary" id="build">Validar e regenerar JSON</button><span class="status" id="buildstatus"></span></div></div></main></div><script>
let units=[],current=null; const $=x=>document.getElementById(x);
async function load(){units=await (await fetch('/api/units')).json(); render();}
function render(){let q=$('q').value.toLowerCase().trim(); let rows=units.filter(u=>!q||u.id.toLowerCase().includes(q)||u.bororo.toLowerCase().includes(q)||u.portuguese.toLowerCase().includes(q)).slice(0,300); $('list').innerHTML=rows.map(u=>`<div class="unit ${current&&current.id===u.id?'on':''}" data-id="${u.id}"><div class=id>${u.id}</div><div class=bor>${esc(u.bororo).slice(0,180)}</div></div>`).join(''); document.querySelectorAll('.unit').forEach(e=>e.onclick=()=>select(e.dataset.id));}
function esc(s){let d=document.createElement('div');d.textContent=s;return d.innerHTML}
function select(id){current=units.find(u=>u.id===id);$('empty').hidden=true;$('card').hidden=false;$('uid').textContent=current.id;$('bp').textContent=current.bororo;$('pp').textContent=current.portuguese;$('be').value=current.bororo;$('pe').value=current.portuguese;$('status').textContent='';render()}
$('q').oninput=render;$('reset').onclick=()=>select(current.id);
$('save').onclick=async()=>{if(!current)return; let r=await fetch('/api/save',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:current.id,bororo:$('be').value,portuguese:$('pe').value})});let x=await r.json();if(!r.ok){$('status').textContent='Erro: '+x.error;return}$('status').textContent='Salvo no TSV.';await load();select(x.id)};
$('build').onclick=async()=>{ $('buildstatus').textContent='Validando…';let r=await fetch('/api/build',{method:'POST'});let x=await r.json();$('buildstatus').textContent=r.ok?'OK: '+x.output:'Erro: '+x.error};load();
</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return
    def send_json(self, obj, status=200):
        data=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/":
            data=PAGE.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data); return
        if p=="/api/units": self.send_json(read_units()); return
        self.send_error(404)
    def do_POST(self):
        p=urlparse(self.path).path
        if p=="/api/save":
            try:
                n=int(self.headers.get("Content-Length","0")); body=json.loads(self.rfile.read(n)); uid=str(body.get("id","")).strip(); bor=str(body.get("bororo","")).strip(); por=str(body.get("portuguese","")).strip()
                if not uid or not bor: raise ValueError("ID e texto Bororo não podem ficar vazios")
                units=read_units(); matches=[u for u in units if u["id"]==uid]
                if len(matches)!=1: raise ValueError("ID estável não encontrado ou duplicado")
                matches[0]["bororo"]=bor; matches[0]["portuguese"]=por; write_units(units); self.send_json({"ok":True,"id":uid}); return
            except Exception as e: self.send_json({"error":str(e)},400); return
        if p=="/api/build":
            try:
                cp=subprocess.run([sys.executable,str(BUILD)],cwd=ROOT,text=True,capture_output=True,check=True); self.send_json({"ok":True,"output":cp.stdout.strip()}); return
            except subprocess.CalledProcessError as e: self.send_json({"error":(e.stderr or e.stdout).strip()},400); return
        self.send_error(404)


def main():
    if not TSV.exists(): raise SystemExit(f"Canonical TSV not found: {TSV}")
    url=f"http://{HOST}:{PORT}"
    server=ThreadingHTTPServer((HOST,PORT),Handler)
    print(f"CorBo Editor: {url}")
    print("Press Ctrl-C to stop. Changes are local until you commit/push them with Git.")
    threading.Timer(.6,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=="__main__": main()
