#!/usr/bin/env python3
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/"CorBo_vNext/texts/historia-mitica/archive_parallel_witnesses.tsv"
P=ROOT/"docs/data/corbo-units.json"
pairs={"BAKD.048":["BOR-CORBO-BM-1CO-012-021"],"BAKD.051":["PAND.038"],"BAKD.059":["PAND.085"],"BAKD.060":["PAND.082"],"BAKD.061":["BARU.021"],"BAKD.064":["PAND.038"]}
with W.open(encoding="utf-8") as f: wr={r["witness_id"]:r for r in csv.DictReader(f,delimiter="\t")}
raw=json.loads(P.read_text(encoding="utf-8")); units=raw if isinstance(raw,list) else raw.get("units",[])
pu={str(u.get("id","")):u for u in units}
def get(u,*ks):
 for k in ks:
  if u.get(k): return str(u[k])
 return ""
for wid,ids in pairs.items():
 r=wr[wid]; print("\n===",wid,"==="); print("B-BOR:",r["source"].replace("\\n"," ")); print("B-POR:",r["portuguese"].replace("\\n"," "))
 for uid in ids:
  u=pu.get(uid,{})
  print("\n["+uid+"]"); print("P-BOR:",get(u,"b","bororo","text","source","reviewed").replace("\\n"," ")); print("P-POR:",get(u,"p","portuguese","text_por","translation").replace("\\n"," "))
