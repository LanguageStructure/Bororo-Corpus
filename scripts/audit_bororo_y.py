#!/usr/bin/env python3
"""Audit legacy y in Bororo-bearing corpus fields only.

Does not touch Portuguese/English metadata, filenames, code, URLs, or citations.
Use --write only for an intentional corpus migration.
"""
from pathlib import Path
import argparse,re

def norm(s): return s.replace("Y","U").replace("y","u")

def conllu(path,write=False):
    text=path.read_text(encoding="utf-8"); out=[]; hits=0
    for line in text.splitlines(True):
        new=line
        if line.startswith("# text ="):
            val=line.split("=",1)[1]
            if re.search(r"[Yy]",val): hits+=1; new=line.split("=",1)[0]+"="+norm(val)
        elif line and not line.startswith("#") and "\t" in line:
            cols=line.rstrip("\n").split("\t")
            if len(cols)>=3:
                for i in (1,2):
                    if re.search(r"[Yy]",cols[i]): hits+=1; cols[i]=norm(cols[i])
                new="\t".join(cols)+"\n"
        out.append(new)
    if write and hits: path.write_text("".join(out),encoding="utf-8")
    return hits

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--write",action="store_true");ap.add_argument("paths",nargs="+");a=ap.parse_args()
    total=0
    for raw in a.paths:
        p=Path(raw)
        if p.suffix==".conllu":
            n=conllu(p,a.write);total+=n
            if n: print(f"{p}: {n} Bororo FORM/LEMMA/# text field(s) with y")
    print(f"total: {total}")
if __name__=="__main__": main()
