from pathlib import Path
import re
P=Path("CorBo/Corpus_Files/CorBo.conllu")
FORMS={"akore","egore","inagore","imagore","akogodure"}
blocks=re.split(r"(\n\s*\n)",P.read_text())
changed=[]
for bi in range(0,len(blocks),2):
 b=blocks[bi]; lines=b.splitlines(); rows=[]
 for i,l in enumerate(lines):
  x=l.split("\t")
  if len(x)==10: rows.append((i,x))
 remove=set()
 for j in range(1,len(rows)):
  if rows[j][1][1]==":" and rows[j-1][1][1].lower() in FORMS: remove.add(int(rows[j][1][0]))
 if not remove: continue
 sid=next((l.split("=",1)[1].strip() for l in lines if l.startswith("# sent_id =")),"?")
 for rid in sorted(remove,reverse=True):
  idx=next(i for i,x in rows if int(x[0])==rid); del lines[idx]
  for k,l in enumerate(lines):
   x=l.split("\t")
   if len(x)!=10: continue
   if not x[0].isdigit(): continue
   oid=int(x[0]); head=x[6]
   if oid>rid:x[0]=str(oid-1)
   if head.isdigit():
    h=int(head)
    if h>rid:x[6]=str(h-1)
    elif h==rid:x[6]="_";x[7]="_"
   lines[k]="\t".join(x)
  for k,l in enumerate(lines):
   if l.startswith("# text ="):
    t=l.split("=",1)[1].strip();t=re.sub(r"(?i)\b(akore|egore|inagore|imagore|akogodure)\s*:",r"\1",t);lines[k]="# text = "+t
 changed.append(sid);blocks[bi]="\n".join(lines)
P.write_text("".join(blocks))
print("Sentenças alteradas:",len(changed));print(*changed,sep="\n")
