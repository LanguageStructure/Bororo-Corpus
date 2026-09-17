#!/usr/bin/env python3
"""Build derived CorBo web indexes from canonical/editorial TSV data.

Coqueiro is canonical reviewed data. História Mítica is published as a work in
progress: reviewed text is used when present; otherwise witness A is exposed as
provisional. Source witnesses remain in the editorial TSV and are not collapsed.
"""
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COQ=ROOT/'CorBo_vNext/texts/coqueiro/coqueiro_parallel.tsv'
HM=ROOT/'CorBo_vNext/texts/historia-mitica/historia_mitica_collation.tsv'
OUT=ROOT/'docs/data'; TOKEN_RE=re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?",re.UNICODE)

def tokens(t):return [m.group(0).lower() for m in TOKEN_RE.finditer(t or '')]
def tsv(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def require(rows,fields,path):
 if not rows:raise SystemExit(f'No rows in {path}')
 missing=[x for x in fields if x not in rows[0]]
 if missing:raise SystemExit(f'Missing columns in {path}: '+', '.join(missing))
def validate(units):
 ids=[]
 for u in units:
  if not u['id']:raise SystemExit('Blank corpus ID')
  if not u['b']:raise SystemExit(f"Blank Bororo text: {u['id']}")
  ids.append(u['id'])
 dup=sorted({x for x in ids if ids.count(x)>1})
 if dup:raise SystemExit('Duplicate corpus IDs: '+', '.join(dup[:20]))
def forms(units):
 c=Counter();uc=Counter()
 for u in units:
  ts=tokens(u['b']);c.update(ts);uc.update(set(ts))
 return [{'form':f,'frequency':n,'units':uc[f]} for f,n in sorted(c.items(),key=lambda x:(-x[1],x[0]))]
def main():
 if not COQ.exists():raise SystemExit(f'Canonical TSV not found: {COQ}')
 cr=tsv(COQ);require(cr,['id','bororo','portuguese'],COQ)
 coq=[{'id':r['id'].strip(),'b':r['bororo'].strip(),'p':r['portuguese'].strip(),'collection':'Coqueiro','reviewed':True} for r in cr]
 hm=[]
 if HM.exists():
  hr=tsv(HM);require(hr,['id','witness_a','witness_b','reviewed','portuguese'],HM)
  for r in hr:
   rev=(r.get('reviewed') or '').strip();base=(r.get('witness_a') or '').strip()
   hm.append({'id':(r.get('id') or '').strip(),'b':rev or base,'p':(r.get('portuguese') or '').strip(),'collection':'História Mítica','reviewed':bool(rev),'status':'reviewed' if rev else 'provisional'})
 allu=coq+hm;validate(allu);OUT.mkdir(parents=True,exist_ok=True)
 for name,data in [('coqueiro-units.json',coq),('historia-mitica-units.json',hm),('corbo-units.json',allu)]:
  (OUT/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 fs=forms(allu);stats={'units':len(allu),'tokens':sum(x['frequency'] for x in fs),'types':len(fs),'collections':['Coqueiro']+(['História Mítica'] if hm else []),'reviewed_units':sum(1 for u in allu if u['reviewed']),'provisional_units':sum(1 for u in allu if not u['reviewed']),'top_forms':fs}
 (OUT/'corbo-stats.json').write_text(json.dumps(stats,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 # retain legacy Coqueiro statistics for pages that have not yet migrated
 cf=forms(coq);cs={'units':len(coq),'tokens':sum(x['frequency'] for x in cf),'types':len(cf),'collections':['Coqueiro'],'top_forms':cf}
 (OUT/'coqueiro-stats.json').write_text(json.dumps(cs,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print(f"Built {len(allu)} units ({len(coq)} Coqueiro, {len(hm)} História Mítica; {stats['provisional_units']} provisional)")
if __name__=='__main__':main()
