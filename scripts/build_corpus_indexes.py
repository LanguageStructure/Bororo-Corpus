#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COQ=ROOT/'CorBo_vNext/texts/coqueiro/coqueiro_parallel.tsv'; HM=ROOT/'CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv'; ADU=ROOT/'CorBo_vNext/texts/adugo-biri/adugo_biri_parallel.tsv'; BOE=ROOT/'CorBo_vNext/texts/boe-ero/boe_ero_parallel.tsv'; MORPH=ROOT/'CorBo_vNext/annotations/morphology.tsv'; CONLLU=ROOT/'CorBo/Corpus_Files/Bororo_UD_enriched_v5_plus_scripture.conllu'; OUT=ROOT/'docs/data'
BIBLES={'jonas':('Jonas','CorBo/Corpus_Files/bíblia/jonas_2-orthophon.txt','CorBo_vNext/texts/biblia/jonas_review.tsv','JON'),'ageu':('Ageu','CorBo/Corpus_Files/bíblia/ageu_2-orthophon.txt','CorBo_vNext/texts/biblia/ageu_review.tsv','AGE'),'cantico':('Cântico dos Cânticos','CorBo/Corpus_Files/bíblia/cantico_dos_canticos_2-orthophon.txt','CorBo_vNext/texts/biblia/cantico_review.tsv','CAN')}
TOKEN_RE=re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?",re.UNICODE)
def tokens(t):return [m.group(0).lower() for m in TOKEN_RE.finditer(t or '')]
def tsv(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def require(rows,fields,path):
 if not rows:return
 missing=[x for x in fields if x not in rows[0]]
 if missing:raise SystemExit(f'Colunas ausentes em {path}: '+', '.join(missing))
def validate(units):
 ids=[u['id'] for u in units]
 if any(not x for x in ids):raise SystemExit('ID de corpus vazio')
 if any(not u['b'] and not u.get('allow_empty_b') for u in units):raise SystemExit('Texto Bororo vazio')
 if len(ids)!=len(set(ids)):raise SystemExit('IDs duplicados no corpus')
def forms(units):
 c=Counter();uc=Counter()
 for u in units:
  ts=tokens(u['b']);c.update(ts);uc.update(set(ts))
 return [{'form':f,'frequency':n,'units':uc[f]} for f,n in sorted(c.items(),key=lambda x:(-x[1],x[0]))]
def misc_dict(s):
 d={}
 if not s or s=='_':return d
 for item in s.split('|'):
  if '=' in item:k,v=item.split('=',1);d[k]=v
 return d
def conllu_relations(path):
 if not path.exists():return []
 acc={}
 with path.open(encoding='utf-8') as f:
  for line in f:
   if not line or line[0]=='#' or line.isspace():continue
   cols=line.rstrip('\n').split('\t')
   if len(cols)!=10 or '-' in cols[0] or '.' in cols[0] or not cols[0].isdigit():continue
   form,lemma,upos,xpos=cols[1],cols[2],cols[3],cols[4];md=misc_dict(cols[9]);ortho=md.get('ORTHO') or form
   if not ortho or ortho=='_' or not re.search(r'[A-Za-zÀ-ÿ]',ortho) or '<' in ortho or '"' in ortho:continue
   key=ortho.casefold();a=acc.setdefault(key,{'form':ortho,'frequency':0,'lemmas':Counter(),'upos':Counter(),'pos_detalhada':Counter(),'glossas':Counter(),'classes_posse':Counter(),'procliticos':Counter()});a['frequency']+=1
   for field,val in [('lemmas',lemma),('upos',upos),('pos_detalhada',md.get('POS_FINE') or xpos),('glossas',md.get('GLOSS')),('classes_posse',md.get('CLS')),('procliticos',md.get('PRCLITIC'))]:
    if val and val!='_':a[field][val]+=1
 out=[]
 for a in acc.values():
  row={'form':a['form'],'frequency':a['frequency']}
  for field in ['lemmas','upos','pos_detalhada','glossas','classes_posse','procliticos']:row[field]=[{'value':v,'frequency':n} for v,n in a[field].most_common()]
  out.append(row)
 return sorted(out,key=lambda x:(-x['frequency'],x['form'].casefold()))
def morphology_data():
 editorial=[]
 if MORPH.exists():
  editorial=[{k:(r.get(k) or '').strip() for k in ['form','segmentation','morphemes','gloss','status','note']} for r in tsv(MORPH)]
 return {'fonte_conllu':str(CONLLU.relative_to(ROOT)),'segmentacao_inferida':False,'relacoes_lexicais':conllu_relations(CONLLU),'analises_editoriais':editorial}
def bible_units():
 out=[]
 for key,(title,src,review,prefix) in BIBLES.items():
  paras=[x.strip() for x in re.split(r'\n\s*\n',(ROOT/src).read_text(encoding='utf-8')) if x.strip()]
  rp=ROOT/review; edits={r['id']:r for r in tsv(rp)} if rp.exists() else {}
  for i,source in enumerate(paras,1):
   uid=f'BOR-CORBO-BIB-{prefix}-{i:04d}';e=edits.get(uid,{});rev=(e.get('reviewed') or '').strip();out.append({'id':uid,'b':rev or source,'source':source,'p':(e.get('portuguese') or '').strip(),'collection':title,'group':'Textos bíblicos','reviewed':bool(rev),'status':'reviewed' if rev else 'provisional','editor_key':key})
 return out
def main():
 cr=tsv(COQ);coq=[{'id':r['id'].strip(),'b':r['bororo'].strip(),'p':r['portuguese'].strip(),'collection':'Coqueiro','reviewed':True} for r in cr]
 hm=[]
 if HM.exists():
  for r in tsv(HM):
   rev=(r.get('reviewed') or '').strip();hm.append({'id':r['id'].strip(),'b':rev or r['witness_a'].strip(),'p':(r.get('portuguese') or '').strip(),'collection':'História Mítica','reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 adu=[]
 if ADU.exists():
  for r in tsv(ADU):
   rev=(r.get('reviewed') or '').strip();src=(r.get('source') or '').strip();adu.append({'id':r['id'].strip(),'b':rev or src,'source':src,'p':(r.get('portuguese') or '').strip(),'collection':'Adugo Biri','reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 boe=[]
 if BOE.exists():
  for r in tsv(BOE):
   rev=(r.get('reviewed') or '').strip();src=(r.get('source') or '').strip();boe.append({'id':r['id'].strip(),'b':rev or src,'source':src,'p':(r.get('portuguese') or '').strip(),'collection':'Boe Ero','allow_empty_b':not bool(src),'section':(r.get('section') or '').strip(),'title':(r.get('title') or '').strip(),'speaker':(r.get('speaker') or '').strip(),'translator':(r.get('translator') or '').strip(),'reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 bib=bible_units();allu=coq+hm+adu+boe+bib;validate(allu);OUT.mkdir(parents=True,exist_ok=True)
 outputs={'coqueiro-units.json':coq,'historia-mitica-units.json':hm,'adugo-biri-units.json':adu,'boe-ero-units.json':boe,'biblia-units.json':bib,'corbo-units.json':allu}
 for name,data in outputs.items():(OUT/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 fs=forms(allu);stats={'units':len(allu),'tokens':sum(x['frequency'] for x in fs),'types':len(fs),'collections':sorted(set(u['collection'] for u in allu)),'reviewed_units':sum(u['reviewed'] for u in allu),'provisional_units':sum(not u['reviewed'] for u in allu),'top_forms':fs};(OUT/'corbo-stats.json').write_text(json.dumps(stats,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 cf=forms(coq);(OUT/'coqueiro-stats.json').write_text(json.dumps({'units':len(coq),'tokens':sum(x['frequency'] for x in cf),'types':len(cf),'collections':['Coqueiro'],'top_forms':cf},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 md=morphology_data();payload=json.dumps(md,ensure_ascii=False,separators=(',',':'));(OUT/'morphology.json').write_text(payload,encoding='utf-8')
 if not md['relacoes_lexicais']:raise SystemExit('Nenhuma relação foi extraída do CoNLL-U.')
 print(f'Geradas {len(allu)} unidades, incluindo {len(bib)} bíblicas, e {len(md["relacoes_lexicais"])} formas CoNLL-U.')
if __name__=='__main__':main()
