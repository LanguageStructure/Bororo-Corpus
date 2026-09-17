#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os índices públicos do CorBo a partir das fontes canônicas/editoriais.

A morfologia lexical é extraída do CoNLL-U (lema, POS, glossa, classe de posse
e proclítico). A segmentação morfológica NÃO é inferida: análises editoriais em
morphology.tsv funcionam como uma camada explícita de revisão/complementação.
"""
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COQ=ROOT/'CorBo_vNext/texts/coqueiro/coqueiro_parallel.tsv'
HM=ROOT/'CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv'
MORPH=ROOT/'CorBo_vNext/annotations/morphology.tsv'
CONLLU=ROOT/'CorBo/Corpus_Files/Bororo_UD_enriched_v5_plus_scripture.conllu'
OUT=ROOT/'docs/data'; TOKEN_RE=re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?",re.UNICODE)
def tokens(t):return [m.group(0).lower() for m in TOKEN_RE.finditer(t or '')]
def tsv(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def require(rows,fields,path):
 if not rows:raise SystemExit(f'Nenhuma linha em {path}')
 missing=[x for x in fields if x not in rows[0]]
 if missing:raise SystemExit(f'Colunas ausentes em {path}: '+', '.join(missing))
def validate(units):
 ids=[]
 for u in units:
  if not u['id']:raise SystemExit('ID de corpus vazio')
  if not u['b']:raise SystemExit(f"Texto Bororo vazio: {u['id']}")
  ids.append(u['id'])
 dup=sorted({x for x in ids if ids.count(x)>1})
 if dup:raise SystemExit('IDs duplicados: '+', '.join(dup[:20]))
def forms(units):
 c=Counter();uc=Counter()
 for u in units:
  ts=tokens(u['b']);c.update(ts);uc.update(set(ts))
 return [{'form':f,'frequency':n,'units':uc[f]} for f,n in sorted(c.items(),key=lambda x:(-x[1],x[0]))]
def misc_dict(s):
 d={}
 if not s or s=='_':return d
 for item in s.split('|'):
  if '=' in item:
   k,v=item.split('=',1);d[k]=v
 return d
def conllu_relations(path):
 if not path.exists():return []
 acc={}
 with path.open(encoding='utf-8') as f:
  for line in f:
   if not line or line[0]=='#' or line.isspace():continue
   cols=line.rstrip('\n').split('\t')
   if len(cols)!=10 or '-' in cols[0] or '.' in cols[0]:continue
   form,lemma,upos,xpos=cols[1],cols[2],cols[3],cols[4];md=misc_dict(cols[9]);ortho=md.get('ORTHO') or form
   if not ortho or ortho=='_':continue
   key=ortho.casefold()
   if key not in acc:acc[key]={'form':ortho,'frequency':0,'lemmas':Counter(),'upos':Counter(),'pos_detalhada':Counter(),'glossas':Counter(),'classes_posse':Counter(),'procliticos':Counter()}
   a=acc[key];a['frequency']+=1
   for field,val in [('lemmas',lemma),('upos',upos),('pos_detalhada',md.get('POS_FINE') or xpos),('glossas',md.get('GLOSS')),('classes_posse',md.get('CLS')),('procliticos',md.get('PRCLITIC'))]:
    if val and val!='_':a[field][val]+=1
 out=[]
 for a in acc.values():
  row={'form':a['form'],'frequency':a['frequency']}
  for field in ['lemmas','upos','pos_detalhada','glossas','classes_posse','procliticos']:row[field]=[{'value':v,'frequency':n} for v,n in a[field].most_common()]
  out.append(row)
 return sorted(out,key=lambda x:(-x['frequency'],x['form'].casefold()))
def morphology_data():
 lexical=conllu_relations(CONLLU);editorial=[]
 if MORPH.exists():
  mr=tsv(MORPH);require(mr,['form','segmentation','morphemes','gloss','status','note'],MORPH)
  editorial=[{k:(r.get(k) or '').strip() for k in ['form','segmentation','morphemes','gloss','status','note']} for r in mr]
 return {'fonte_conllu':str(CONLLU.relative_to(ROOT)) if CONLLU.exists() else None,'segmentacao_inferida':False,'relacoes_lexicais':lexical,'analises_editoriais':editorial}
def main():
 if not COQ.exists():raise SystemExit(f'TSV canônico não encontrado: {COQ}')
 cr=tsv(COQ);require(cr,['id','bororo','portuguese'],COQ);coq=[{'id':r['id'].strip(),'b':r['bororo'].strip(),'p':r['portuguese'].strip(),'collection':'Coqueiro','reviewed':True} for r in cr]
 hm=[]
 if HM.exists():
  hr=tsv(HM);require(hr,['id','witness_a','witness_b','reviewed','portuguese'],HM)
  for r in hr:
   rev=(r.get('reviewed') or '').strip();base=(r.get('witness_a') or '').strip();hm.append({'id':(r.get('id') or '').strip(),'b':rev or base,'p':(r.get('portuguese') or '').strip(),'collection':'História Mítica','reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 allu=coq+hm;validate(allu);OUT.mkdir(parents=True,exist_ok=True)
 for name,data in [('coqueiro-units.json',coq),('historia-mitica-units.json',hm),('corbo-units.json',allu)]:(OUT/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 fs=forms(allu);stats={'units':len(allu),'tokens':sum(x['frequency'] for x in fs),'types':len(fs),'collections':['Coqueiro']+(['História Mítica'] if hm else []),'reviewed_units':sum(1 for u in allu if u['reviewed']),'provisional_units':sum(1 for u in allu if not u['reviewed']),'top_forms':fs};(OUT/'corbo-stats.json').write_text(json.dumps(stats,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 cf=forms(coq);cs={'units':len(coq),'tokens':sum(x['frequency'] for x in cf),'types':len(cf),'collections':['Coqueiro'],'top_forms':cf};(OUT/'coqueiro-stats.json').write_text(json.dumps(cs,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 md=morphology_data();payload=json.dumps(md,ensure_ascii=False,separators=(',',':'));(OUT/'morphology.json').write_text(payload,encoding='utf-8')
 if not md['relacoes_lexicais']:raise SystemExit('Nenhuma relação foi extraída do CoNLL-U; morphology.json não será publicado vazio.')
 print(f"Geradas {len(allu)} unidades e {len(md['relacoes_lexicais'])} formas com relações do CoNLL-U ({len(payload)} bytes de morfologia).")
if __name__=='__main__':main()
