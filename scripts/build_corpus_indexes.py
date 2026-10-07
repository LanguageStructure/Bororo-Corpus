#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COQ=ROOT/'CorBo_vNext/texts/coqueiro/coqueiro_parallel.tsv'; ETN=ROOT/'CorBo_vNext/texts/etnobotanica/etnobotanica.tsv'; HM=ROOT/'CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv'; ADU=ROOT/'CorBo_vNext/texts/adugo-biri/adugo_biri_parallel.tsv'; BOE=ROOT/'CorBo_vNext/texts/boe-ero/boe_ero_parallel.tsv'; BM=ROOT/'CorBo_vNext/texts/bakaru-maiwu'; BAK=ROOT/'CorBo_vNext/texts/bakarudoge/bakarudoge_documentary.tsv'; PC=ROOT/'CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv'; PC_COL=ROOT/'CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_collation.tsv'; ARC=ROOT/'CorBo_vNext/texts/archive-additions/archive_additions_editorial.tsv'; ARC_COL=ROOT/'CorBo_vNext/texts/archive-additions/archive_additions_collation.tsv'; PAR=ROOT/'CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv'; MORPH=ROOT/'CorBo_vNext/annotations/morphology.tsv'; DICT_ANN=ROOT/'CorBo_vNext/annotations/dictionary_validated_layers.tsv'; DICT_CONLLU=ROOT/'CorBo/Corpus_Files/exemplosDicBor_full_review_pass17_incomplete_first.conllu'; BORORO2_CONLLU=ROOT/'CorBo/Corpus_Files/Bororo2.conllu'; CONLLU=ROOT/'CorBo/Corpus_Files/Bororo_UD_enriched_v5_plus_scripture.conllu'; OUT=ROOT/'docs/data'
BIBLES={'jonas':('Jonas','CorBo/Corpus_Files/bíblia/jonas_2-orthophon.txt','CorBo_vNext/texts/biblia/jonas_review.tsv','JON'),'ageu':('Ageu','CorBo/Corpus_Files/bíblia/ageu_2-orthophon.txt','CorBo_vNext/texts/biblia/ageu_review.tsv','AGE'),'cantico':('Cântico dos Cânticos','CorBo/Corpus_Files/bíblia/cantico_dos_canticos_2-orthophon.txt','CorBo_vNext/texts/biblia/cantico_review.tsv','CAN')}
TOKEN_RE=re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?",re.UNICODE)
def normalize_bororo_y(s):
 return str(s or '').replace('Y','U').replace('y','u')

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
 if len(ids)!=len(set(ids)):
  dup=[x for x,n in Counter(ids).items() if n>1]
  raise SystemExit('IDs duplicados no corpus: '+', '.join(dup[:50]))
def forms(units):
 c=Counter();uc=Counter()
 for u in units:
  ts=tokens(normalize_bororo_y(u['b']));c.update(ts);uc.update(set(ts))
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
def merge_relations(*sources):
 acc={}
 for rows in sources:
  for r in rows:
   key=r['form'].casefold();a=acc.setdefault(key,{'form':r['form'],'frequency':0,'lemmas':Counter(),'upos':Counter(),'pos_detalhada':Counter(),'glossas':Counter(),'classes_posse':Counter(),'procliticos':Counter()});a['frequency']+=r.get('frequency',0)
   for field in ['lemmas','upos','pos_detalhada','glossas','classes_posse','procliticos']:
    for x in r.get(field,[]):a[field][x['value']]+=x['frequency']
 out=[]
 for a in acc.values():
  row={'form':a['form'],'frequency':a['frequency']}
  for field in ['lemmas','upos','pos_detalhada','glossas','classes_posse','procliticos']:row[field]=[{'value':v,'frequency':n} for v,n in a[field].most_common()]
  out.append(row)
 return sorted(out,key=lambda x:(-x['frequency'],x['form'].casefold()))
def conllu_morphemes(path):
 acc={}
 if not path.exists():return []
 with path.open(encoding='utf-8') as f:
  for line in f:
   if not line or line[0]=='#' or line.isspace():continue
   cols=line.rstrip('\n').split('\t')
   if len(cols)!=10 or '-' in cols[0] or '.' in cols[0] or not cols[0].isdigit():continue
   md=misc_dict(cols[9]);form=md.get('ORTHO') or cols[1];seg=md.get('MORPH') or md.get('GLOSS')
   if not seg or seg=='_' or not re.search(r'[-=]',seg):continue
   parts=[p for p in re.split(r'[-=]',seg) if p]
   if len(parts)<2:continue
   for i,m in enumerate(parts):
    key=m.casefold();a=acc.setdefault(key,{'morpheme':m,'frequency':0,'examples':Counter(),'lemmas':Counter(),'upos':Counter(),'xpos':Counter(),'positions':Counter()});a['frequency']+=1;a['examples'][form]+=1
    if cols[2] and cols[2]!='_':a['lemmas'][cols[2]]+=1
    if cols[3] and cols[3]!='_':a['upos'][cols[3]]+=1
    fine=md.get('POS_FINE') or cols[4]
    if fine and fine!='_':a['xpos'][fine]+=1
    if '=' in seg:
     raw=re.split(r'([- =])',seg.replace(' ',''));seen=0
     for j,x in enumerate(raw):
      if x==m:
       left=raw[j-1] if j else '';right=raw[j+1] if j+1<len(raw) else ''
       if left=='=':a['positions']['enclitic']+=1
       elif right=='=':a['positions']['proclitic']+=1
       else:a['positions']['stem_or_affix']+=1
       seen=1;break
     if not seen:a['positions']['stem_or_affix']+=1
    else:a['positions']['stem_or_affix']+=1
 out=[]
 for a in acc.values():
  xpos=a['xpos'].most_common();upos=a['upos'].most_common()
  out.append({'morpheme':a['morpheme'],'frequency':a['frequency'],'examples':[{'value':v,'frequency':n} for v,n in a['examples'].most_common(8)],'lemmas':[{'value':v,'frequency':n} for v,n in a['lemmas'].most_common(8)],'upos':[{'value':v,'frequency':n} for v,n in upos],'xpos':[{'value':v,'frequency':n} for v,n in xpos],'positions':[{'value':v,'frequency':n} for v,n in a['positions'].most_common()],'classe_principal':xpos[0][0] if xpos else (upos[0][0] if upos else ''),'classe_ambigua':len(xpos)>1 or (not xpos and len(upos)>1)})
 return sorted(out,key=lambda x:(-x['frequency'],x['morpheme'].casefold()))
MORPHEME_KNOWLEDGE={
 're':{'gloss':'IND','class':'mood','label':'indicativo','status':'confirmed'},
 'wu':{'gloss':'NOMZR/REL','class':'derivation','label':'nominalizador/relativizador','status':'confirmed'},
 'ge':{'gloss':'PL','class':'number','label':'plural','status':'confirmed'},
 'modu':{'gloss':'IRR','class':'mood','label':'irrealis','status':'confirmed'},
 'godu':{'gloss':'INC','class':'aspect','label':'incoativo','status':'confirmed'},
 'i':{'gloss':'1.SG','class':'person_index','label':'índice pessoal de 1ª pessoa singular','status':'confirmed'},
 'u':{'gloss':'3.SG','class':'person_index','label':'índice pessoal de 3ª pessoa singular','status':'confirmed'},
 'pa':{'gloss':'1.PL.IN','class':'person_index','label':'índice pessoal de 1ª pessoa plural inclusiva','status':'confirmed'},
 'ce':{'gloss':'1.PL.EX','class':'person_index','label':'índice pessoal de 1ª pessoa plural exclusiva','status':'confirmed'},
 'e':{'gloss':'3.PL','class':'person_index','label':'índice pessoal de 3ª pessoa plural','status':'confirmed'},
 'ji':{'gloss':'POSP','class':'posp','label':'posposição','status':'confirmed','note':'Função/semântica específica varia conforme a construção.'},
 'doge':{'gloss':'PL','class':'number','label':'plural','status':'confirmed'},
 'nu':{'gloss':'PROG','class':'aspect','label':'progressivo','status':'confirmed'},
 'ka':{'gloss':'NEG','class':'polarity','label':'negação','status':'provisional','note':'Registrado em segmentações como pega-ka-re, kuri-ka-re, mori-ka-re e nudu-ka-re; manter para revisão editorial.'},
 'do':{'gloss':'?','class':'suffix','label':'sufixo -do','status':'provisional','note':'Segmentado em formas como aiwo-do, pemega-do e barare-do; função não consolidada automaticamente.'},
 'wa':{'gloss':'?','class':'suffix','label':'sufixo -wa','status':'provisional','note':'Segmentado em jorudu-wa e jorudui-wa; função requer revisão.'},
 'wo':{'gloss':'?','class':'suffix','label':'sufixo -wo','status':'provisional','note':'Segmentado em botu-wo, mugu-wo e outras formas; função requer revisão.'},
 'du':{'gloss':'?','class':'suffix','label':'morfema -du','status':'provisional','note':'Recorrente em segmentações; há também usos independentes/proclíticos, portanto não unificados automaticamente.'},
 'ie':{'gloss':'?','class':'suffix','label':'sufixo -ie','status':'provisional','note':'Segmentado em formas verbais como meru-ie e motu-ie; análise funcional deve ser revista.'},
 'tu':{'gloss':'?','class':'person_index','label':'proclítico tu=','status':'provisional','note':'PRCLITIC=tu= ocorre no léxico enriquecido; valor gramatical deve ser confirmado editorialmente.'},
 'ta':{'gloss':'?','class':'person_index','label':'proclítico ta=','status':'provisional','note':'PRCLITIC=ta= ocorre no léxico enriquecido; valor gramatical deve ser confirmado editorialmente.'}
}
def enrich_morphemes(rows):
 for r in rows:
  k=r['morpheme'].casefold()
  if k in MORPHEME_KNOWLEDGE:r['analysis']=MORPHEME_KNOWLEDGE[k]
 return rows
def conllu_sentences(path, namespace=''):
 out=[];meta={};rows=[];sid_counts={}
 def flush():
  nonlocal meta,rows
  if not rows:
   meta={};rows=[];return
  sid=meta.get('sent_id')
  if not sid:
   meta={};rows=[];return
  text=meta.get('text') or ' '.join(x['form'] for x in rows)
  original_sid=sid
  if namespace:
   sid_counts[original_sid]=sid_counts.get(original_sid,0)+1
   n=sid_counts[original_sid]
   sid=f"{namespace}:{original_sid}" + (f"#{n}" if n>1 else "")
  out.append({'sent_id':sid,'sent_id_original':original_sid,'text':text,'text_por':meta.get('text_por',''),'text_eng':meta.get('text_eng',''),'source_conllu':path.name,'tokens':rows})
  meta={};rows=[]
 if not path.exists():return out
 with path.open(encoding='utf-8') as f:
  for line in f:
   line=line.rstrip('\n')
   if not line.strip():flush();continue
   if line.startswith('#'):
    if re.match(r'#\s*sent_id\s*=',line) and rows:flush()
    m=re.match(r'#\s*([^=]+?)\s*=\s*(.*)$',line)
    if m:meta[m.group(1).strip()]=m.group(2).strip()
    continue
   cols=line.split('\t')
   if len(cols)!=10 or '-' in cols[0] or '.' in cols[0] or not cols[0].isdigit():continue
   md=misc_dict(cols[9]);rows.append({'id':int(cols[0]),'form':cols[1],'lemma':cols[2],'upos':cols[3],'xpos':cols[4],'feats':cols[5],'head':int(cols[6]) if cols[6].isdigit() else None,'deprel':cols[7],'deps':cols[8],'misc':md})
  flush()
 return out
def pending_annotations(path):
 out=[]; annotated=set(); pending=[]
 blocks=re.split(r"(?=^# *sent_id *=)",path.read_text(encoding="utf-8"),flags=re.M)
 for b in blocks:
  m=re.search(r"^# *text *= *(.*)$",b,re.M)
  if not m:continue
  text=m.group(1).strip()
  sid=re.search(r"^# *sent_id *= *(.*)$",b,re.M)
  if re.search(r"^[0-9]+\t",b,re.M):annotated.add(text)
  else:pending.append((sid.group(1).strip() if sid else "",text))
 seen=set()
 for sid,text in pending:
  if text in annotated or text in seen:continue
  seen.add(text)
  out.append({"sent_id":sid,"text":text,"source_conllu":path.name,"status":"editorial_review" if sid=="542-3" else "pending_annotation"})
 return out

def generator_attested_forms(path):
 """Inventory explicit CoNLL-U token analyses for the experimental generator.

 This is evidence, not a productive grammar: no segmentation, feature or
 paradigm cell is inferred here.
 """
 sentences=conllu_sentences(path);acc={}
 for s in sentences:
  sid=s.get('sent_id','')
  for t in s.get('tokens',[]):
   form=t.get('form','');lemma=t.get('lemma','');feats=t.get('feats','')
   if not form or form=='_' or not lemma or lemma=='_':continue
   if not re.search(r'[A-Za-zÀ-ÿ]',form):continue
   key=(form.casefold(),lemma.casefold(),t.get('upos',''),t.get('xpos',''),feats or '_')
   a=acc.setdefault(key,{'form':form,'lemma':lemma,'upos':t.get('upos',''),'xpos':t.get('xpos',''),'feats':feats or '_','frequency':0,'evidence':[]})
   a['frequency']+=1
   if sid and sid not in a['evidence']:a['evidence'].append(sid)
 out=list(acc.values())
 for a in out:
  a['status']='attested'
  a['evidence']=a['evidence'][:20]
 return sorted(out,key=lambda x:(x['lemma'].casefold(),x['form'].casefold(),x['feats']))

def annotation_completeness(row):
 lexical=bool(row.get('lemma') and row.get('upos'))
 morphology=bool(row.get('feats'))
 syntax=bool(row.get('head') and row.get('deprel'))
 return {'lexical':lexical,'morphology':morphology,'syntax':syntax}
def dictionary_annotation_data():
 # Combine token-level annotation from dictionary and Bororo2.
 out=[];seen=set()
 def read_conllu(path,namespace=''):
  if not path.exists():return
  sent_id='';sid_counts={}
  def emit(cols,sid):
   if len(cols)!=10 or '-' in cols[0] or '.' in cols[0] or not cols[0].isdigit():return
   form,lemma,upos,xpos,feats,head,deprel=cols[1],cols[2],cols[3],cols[4],cols[5],cols[6],cols[7]
   vals={'sent_id':sid,'token_id':cols[0],'form':form,'lemma':'' if lemma=='_' else lemma,'upos':'' if upos=='_' else upos,'xpos':'' if xpos=='_' else xpos,'feats':'' if feats=='_' else feats,'head':'' if head=='_' else head,'deprel':'' if deprel=='_' else deprel,'source':path.name}
   # Keep a token when at least one explicit linguistic layer is present.
   if not any(vals[k] for k in ['lemma','upos','xpos','feats','head','deprel']):return
   vals['layers']=[k for k in ['lemma','upos','xpos','feats'] if vals[k]]
   if vals['head'] and vals['deprel']:vals['layers'].append('syntax')
   vals['complete']=annotation_completeness(vals);out.append(vals);seen.add((sid,cols[0]))
  with path.open(encoding='utf-8') as f:
   for line in f:
    line=line.rstrip('\n')
    if line.startswith('#'):
     m=re.match(r'#\s*sent_id\s*=\s*(.*)$',line)
     if m:
      original=m.group(1).strip()
      sid_counts[original]=sid_counts.get(original,0)+1
      n=sid_counts[original];sent_id=(f'{namespace}:{original}'+(f'#{n}' if n>1 else '')) if namespace else original
    elif line.strip():
     emit(line.split('\t'),sent_id)
 read_conllu(DICT_CONLLU)
 read_conllu(BORORO2_CONLLU,'bororo2')
 if DICT_ANN.exists():
  for r in tsv(DICT_ANN):
   key=((r.get('sent_id') or '').strip(),(r.get('token_id') or '').strip())
   if key in seen:continue
   row={k:(r.get(k) or '').strip() for k in ['sent_id','token_id','form','lemma','upos','xpos','feats','head','deprel','source']}
   row['layers']=[k for k in ['lemma','upos','xpos','feats'] if row[k]]
   if row['head'] and row['deprel']:row['layers'].append('syntax')
   row['complete']=annotation_completeness(row);out.append(row)
 return out
def morpheme_token_data(path, namespace=""):
 """Token-level evidence for morphemes explicitly represented in the current CoNLL-U.

 General segmentation is read only from MISC/GLOSS when it contains explicit
 - or = boundaries. The special -iagu relation is licensed only by Speech=Quo.
 No segmentation is inferred from the surface form.
 """
 out=[]
 for sent in conllu_sentences(path, namespace=namespace):
  sid=sent.get('sent_id','')
  for t in sent.get('tokens',[]):
   md=t.get('misc') or {};seg=md.get('MORPH') or md.get('GLOSS') or '';seg_source='MISC/MORPH' if md.get('MORPH') else 'MISC/GLOSS';form=t.get('form') or ''
   if seg and seg!='_' and re.search(r'[-=]',seg):
    parts=[p for p in re.split(r'[-=]',seg) if p]
    for i,m in enumerate(parts):
     pos='stem_or_affix'
     if '=' in seg:
      raw=re.split(r'([-=])',seg.replace(' ',''))
      for j,x in enumerate(raw):
       if x==m:
        left=raw[j-1] if j else '';right=raw[j+1] if j+1<len(raw) else ''
        if left=='=':pos='enclitic'
        elif right=='=':pos='proclitic'
        break
     out.append({'morpheme':m,'position':pos,'segmentation':seg,'form':form,'sent_id':sid,'token_id':t.get('id'),'lemma':t.get('lemma',''),'upos':t.get('upos',''),'xpos':t.get('xpos',''),'feats':t.get('feats',''),'deprel':t.get('deprel',''),'text':sent.get('text',''),'text_por':sent.get('text_por',''),'evidence':seg_source})
   feats=str(t.get('feats') or '')
   if form.casefold().endswith('iagu') and 'Speech=Quo' in feats:
    out.append({'morpheme':'iagu','position':'suffix','segmentation':'','form':form,'sent_id':sid,'token_id':t.get('id'),'lemma':t.get('lemma',''),'upos':t.get('upos',''),'xpos':t.get('xpos',''),'feats':feats,'deprel':t.get('deprel',''),'text':sent.get('text',''),'text_por':sent.get('text_por',''),'evidence':'FEATS:Speech=Quo'})
 return out

def morphology_data():
 editorial=[]
 if MORPH.exists():
  editorial=[{k:(r.get(k) or '').strip() for k in ['form','segmentation','morphemes','gloss','status','note']} for r in tsv(MORPH)]
 morphs=enrich_morphemes(conllu_morphemes(DICT_CONLLU))
 qi=Counter()
 if DICT_CONLLU.exists():
  with DICT_CONLLU.open(encoding='utf-8') as f:
   for line in f:
    if not line.strip() or line.startswith('#'):continue
    c=line.rstrip('\n').split('\t')
    if len(c)!=10 or '-' in c[0] or '.' in c[0]:continue
    feats=c[5] if c[5]!='_' else ''
    if 'Speech=Quo' in feats and c[2] not in ('','_') and c[1].casefold().endswith('iagu'):
     qi[c[1]]+=1
 if qi:
  morphs.append({'morpheme':'iagu','frequency':sum(qi.values()),'examples':[{'value':v,'frequency':n} for v,n in qi.most_common(20)],'lemmas':[],'upos':[{'value':'PRON','frequency':sum(qi.values())}],'xpos':[],'positions':[{'value':'suffix','frequency':sum(qi.values())}],'classe_principal':'Speech=Quo','classe_ambigua':False,'analysis':{'gloss':'QUO','class':'speech','label':'marcador de fala/citação -iagu','status':'attested','note':'Relação derivada apenas de tokens do pass17 explicitamente anotados com Speech=Quo e forma terminada em iagu.'}})
 return {'fonte_conllu':str(DICT_CONLLU.relative_to(ROOT)),'fontes_lexicais':[str(DICT_CONLLU.relative_to(ROOT)),str(BORORO2_CONLLU.relative_to(ROOT))],'segmentacao_inferida':False,'relacoes_lexicais':merge_relations(conllu_relations(DICT_CONLLU),conllu_relations(BORORO2_CONLLU)),'morfemas_conllu':morphs,'analises_editoriais':editorial}
def etnobotanica_units():
 if not ETN.exists():return []
 out=[]
 for r in tsv(ETN):
  uid=(r.get('id') or '').strip();name=(r.get('name') or '').strip();desc=(r.get('description') or '').strip()
  if not uid or not name:continue
  out.append({'id':uid,'b':desc,'name':name,'p':'','collection':'Etnobotânica','group':'Etnobotânica','reviewed':True,'status':'reviewed','allow_empty_b':not bool(desc)})
 return out
def bible_units():
 out=[]
 for key,(title,src,review,prefix) in BIBLES.items():
  paras=[x.strip() for x in re.split(r'\n\s*\n',(ROOT/src).read_text(encoding='utf-8')) if x.strip()]
  rp=ROOT/review; edits={r['id']:r for r in tsv(rp)} if rp.exists() else {}
  for i,source in enumerate(paras,1):
   uid=f'BOR-CORBO-BIB-{prefix}-{i:04d}';e=edits.get(uid,{});rev=(e.get('reviewed') or '').strip();out.append({'id':uid,'b':rev or source,'source':source,'p':(e.get('portuguese') or '').strip(),'collection':title,'group':'Textos bíblicos','reviewed':bool(rev),'status':'reviewed' if rev else 'provisional','editor_key':key})
 return out
def bakarudoge_documents():
 if not BAK.exists():return []
 return [{k:(r.get(k) or '').strip() for k in ['id','text_number','title','metadata','documentary_content','reviewed','editorial_note']} for r in tsv(BAK)]
def bakaru_units():
 out=[]
 if not BM.exists():return out
 for path in sorted(BM.glob('*/*.tsv')):
  seen=set()
  for r in tsv(path):
   uid=(r.get('id') or '').strip();src=(r.get('source') or '').strip();rev=(r.get('reviewed') or '').strip()
   # The source importer currently emits some repeated verse IDs when a physical-line number is mistaken for a chapter marker.
   # Do not publish ambiguous later occurrences; retain the first documentary occurrence until the importer is regenerated from source.
   if uid in seen:continue
   seen.add(uid)
   # DOC rows are documentary/editorial notes, not linguistic corpus units.
   if not uid or '-DOC-' in uid:continue
   # Bakaru IDs can collide with legacy biblical IDs only if imported twice; keep BM namespace isolated.
   if not uid.startswith('BOR-CORBO-BM-'):
    uid='BOR-CORBO-BM-'+uid.removeprefix('BOR-CORBO-')
   out.append({'id':uid,'b':rev or src,'source':src,'p':'','collection':'Bakaru Maiwu','group':'Novo Testamento','book':(r.get('book') or '').strip(),'book_code':(r.get('book_code') or '').strip(),'chapter':(r.get('chapter') or '').strip(),'verse':(r.get('verse') or '').strip(),'reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 return out
def pemo_coqueiro_units():
 if not PC.exists() or not PC_COL.exists():return []
 editorial={r['id'].strip():r for r in tsv(PC)}
 decisions={r['id'].strip():r for r in tsv(PC_COL)}
 out=[]
 for uid,r in editorial.items():
  d=decisions.get(uid)
  if not d:raise SystemExit(f'Pemo-Coqueiro sem decisão de colação: {uid}')
  status=(d.get('status') or '').strip()
  if status=='confirmed':continue
  if status not in {'unique','parallel_formulaic'}:
   raise SystemExit(f'Pemo-Coqueiro não resolvido para publicação: {uid} ({status})')
  src=(r.get('source') or '').strip();rev=(r.get('reviewed') or '').strip()
  out.append({'id':uid,'b':rev or src,'source':src,'p':(r.get('portuguese') or '').strip(),'collection':'Pemo–Coqueiro','group':'Pemo–Coqueiro','section':(r.get('section') or '').strip(),'source_number':(r.get('source_number') or '').strip(),'editorial_note':(r.get('editorial_note') or '').strip(),'collation_status':status,'reviewed':bool(rev),'status':'reviewed' if rev else 'documentary'})
 return out

def archive_additions_units():
 if not ARC.exists() or not ARC_COL.exists():return []
 editorial={r['id'].strip():r for r in tsv(ARC)}
 decisions={r['id'].strip():r for r in tsv(ARC_COL)}
 out=[]
 for uid,r in editorial.items():
  d=decisions.get(uid)
  if not d:raise SystemExit(f'Archive-additions sem decisão de colação: {uid}')
  status=(d.get('status') or '').strip()
  if status=='confirmed':continue
  if status not in {'unique','parallel_formulaic'}:
   raise SystemExit(f'Archive-additions não resolvido para publicação: {uid} ({status})')
  src=(r.get('source') or '').strip();rev=(r.get('reviewed') or '').strip()
  out.append({'id':uid,'b':rev or src,'source':src,'p':(r.get('portuguese') or '').strip(),'collection':(r.get('document') or 'Archive additions').strip(),'group':'Archive additions','section':(r.get('section') or '').strip(),'source_file':(r.get('source_file') or '').strip(),'source_number':(r.get('source_number') or '').strip(),'editorial_note':(r.get('editorial_note') or '').strip(),'collation_status':status,'reviewed':bool(rev),'status':'reviewed' if rev else 'documentary'})
 return out

def archive_parallel_units():
 if not PAR.exists():return []
 out=[]
 for r in tsv(PAR):
  uid=(r.get('witness_id') or '').strip()
  status=(r.get('collation_status') or '').strip()
  if status in {'confirmed','component','unresolved'}:continue
  if status not in {'unique','parallel_formulaic'}:
   raise SystemExit(f'Archive-parallel não resolvido para publicação: {uid} ({status})')
  src=(r.get('source') or '').strip()
  if not src:raise SystemExit(f'Archive-parallel sem texto-fonte: {uid}')
  out.append({'id':uid,'b':src,'source':src,'p':(r.get('portuguese') or '').strip(),'collection':(r.get('document') or 'Archive parallel witnesses').strip(),'group':'Archive parallel witnesses','section':(r.get('section') or '').strip(),'source_file':(r.get('source_file') or '').strip(),'source_number':(r.get('source_number') or '').strip(),'editorial_note':(r.get('editorial_note') or '').strip(),'collation_status':status,'reviewed':False,'status':'documentary'})
 return out

def collation_data():
 out=[]
 if PC.exists() and PC_COL.exists():
  editorial={r['id'].strip():r for r in tsv(PC)}
  for d in tsv(PC_COL):
   uid=(d.get('id') or '').strip();r=editorial.get(uid,{})
   out.append({'id':uid,'family':'Pemo–Coqueiro','document':'Pemo–Coqueiro','source':(r.get('source') or '').strip(),'portuguese':(r.get('portuguese') or '').strip(),'reviewed':(r.get('reviewed') or '').strip(),'status':(d.get('status') or '').strip(),'corbo_match_id':(d.get('corbo_match_id') or '').strip(),'decision_note':(d.get('decision_note') or '').strip()})
 if PAR.exists():
  for r in tsv(PAR):
   out.append({'id':(r.get('witness_id') or '').strip(),'family':'Testemunhos paralelos de arquivo','document':(r.get('document') or '').strip(),'source':(r.get('source') or '').strip(),'portuguese':(r.get('portuguese') or '').strip(),'reviewed':'','status':(r.get('collation_status') or '').strip(),'corbo_match_id':(r.get('corbo_match_id') or '').strip(),'decision_note':(r.get('editorial_note') or '').strip()})
 return out

def main():
 cr=tsv(COQ);coq=[{'id':r['id'].strip(),'b':r['bororo'].strip(),'p':r['portuguese'].strip(),'collection':'Coqueiro','group':'Documentary texts','reviewed':True,'status':'reviewed'} for r in cr]
 hm=[]
 if HM.exists():
  for r in tsv(HM):
   rev=(r.get('reviewed') or '').strip();hm.append({'id':r['id'].strip(),'b':rev or r['witness_a'].strip(),'p':(r.get('portuguese') or '').strip(),'collection':'História Mítica','group':'Documentary texts','reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 adu=[]
 if ADU.exists():
  for r in tsv(ADU):
   rev=(r.get('reviewed') or '').strip();src=(r.get('source') or '').strip();adu.append({'id':r['id'].strip(),'b':rev or src,'source':src,'p':(r.get('portuguese') or '').strip(),'collection':'Adugo Biri','group':'Documentary texts','reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 boe=[]
 if BOE.exists():
  for r in tsv(BOE):
   rev=(r.get('reviewed') or '').strip();src=(r.get('source') or '').strip();boe.append({'id':r['id'].strip(),'b':rev or src,'source':src,'p':(r.get('portuguese') or '').strip(),'collection':'Boe Ero','group':'Documentary texts','allow_empty_b':not bool(src),'section':(r.get('section') or '').strip(),'title':(r.get('title') or '').strip(),'speaker':(r.get('speaker') or '').strip(),'translator':(r.get('translator') or '').strip(),'source_number':(r.get('source_number') or '').strip(),'translation_number':(r.get('translation_number') or '').strip(),'editorial_note':(r.get('editorial_note') or '').strip(),'reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 bib=bible_units();bm=bakaru_units();etn=etnobotanica_units();pc=pemo_coqueiro_units();arc=archive_additions_units();par=archive_parallel_units();allu=coq+hm+adu+boe+bib+bm+etn+pc+arc+par;validate(allu);OUT.mkdir(parents=True,exist_ok=True)
 bakdocs=bakarudoge_documents();(OUT/'bakarudoge-documents.json').write_text(json.dumps(bakdocs,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 outputs={'coqueiro-units.json':coq,'historia-mitica-units.json':hm,'adugo-biri-units.json':adu,'boe-ero-units.json':boe,'biblia-units.json':bib,'bakaru-maiwu-units.json':bm,'etnobotanica-units.json':etn,'pemo-coqueiro-units.json':pc,'archive-additions-units.json':arc,'archive-parallel-units.json':par,'corbo-units.json':allu}
 for name,data in outputs.items():(OUT/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 fs=forms(allu)
 by_collection=Counter(u.get('collection') or '(sem coleção)' for u in allu)
 by_group=Counter(u.get('group') or '(sem grupo)' for u in allu)
 by_status=Counter(u.get('status') or '(sem status)' for u in allu)
 by_collation=Counter(u.get('collation_status') for u in allu if u.get('collation_status'))
 stats={'units':len(allu),'tokens':sum(x['frequency'] for x in fs),'types':len(fs),'collections':sorted(by_collection),'units_by_collection':dict(sorted(by_collection.items())),'units_by_group':dict(sorted(by_group.items())),'units_by_status':dict(sorted(by_status.items())),'units_by_collation_status':dict(sorted(by_collation.items())),'reviewed_units':sum(bool(u.get('reviewed')) for u in allu),'provisional_units':sum(not bool(u.get('reviewed')) for u in allu),'top_forms':fs};(OUT/'corbo-stats.json').write_text(json.dumps(stats,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 cf=forms(coq);(OUT/'coqueiro-stats.json').write_text(json.dumps({'units':len(coq),'tokens':sum(x['frequency'] for x in cf),'types':len(cf),'collections':['Coqueiro'],'top_forms':cf},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 md=morphology_data();payload=json.dumps(md,ensure_ascii=False,separators=(',',':'));(OUT/'morphology.json').write_text(payload,encoding='utf-8');(OUT/'ud-sentences.json').write_text(json.dumps(conllu_sentences(DICT_CONLLU)+conllu_sentences(BORORO2_CONLLU,namespace='bororo2'),ensure_ascii=False,separators=(',',':')),encoding='utf-8');(OUT/'dictionary-annotations.json').write_text(json.dumps(dictionary_annotation_data(),ensure_ascii=False,separators=(',',':')),encoding='utf-8');(OUT/'morpheme-tokens.json').write_text(json.dumps(morpheme_token_data(DICT_CONLLU)+morpheme_token_data(BORORO2_CONLLU,namespace='bororo2'),ensure_ascii=False,separators=(',',':')),encoding='utf-8');(OUT/'collation.json').write_text(json.dumps(collation_data(),ensure_ascii=False,separators=(',',':')),encoding='utf-8');(OUT/'generator-attested-forms.json').write_text(json.dumps({'source':str(DICT_CONLLU.relative_to(ROOT)),'inferred':False,'forms':generator_attested_forms(DICT_CONLLU)},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 (OUT/'pending-annotations.json').write_text(json.dumps(pending_annotations(BORORO2_CONLLU),ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 if not md['relacoes_lexicais']:raise SystemExit('Nenhuma relação foi extraída do CoNLL-U.')
 print(f'Geradas {len(allu)} unidades, incluindo {len(bib)} bíblicas, {len(bm)} do Bakaru Maiwu, {len(etn)} de Etnobotânica e {len(pc)} de Pemo–Coqueiro, {len(arc)} de Archive additions, {len(par)} de Archive parallel witnesses, e {len(md["relacoes_lexicais"])} formas CoNLL-U.')
if __name__=='__main__':main()
