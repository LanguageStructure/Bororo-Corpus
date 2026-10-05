#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build persistent human collation decisions for Pemo-Coqueiro.

This file records decisions already established during manual/sequence review.
It does not alter the editorial witness or the public corpus.
"""
from __future__ import annotations
import csv,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_editorial.tsv"
OUT=ROOT/"CorBo_vNext/texts/pemo-coqueiro/pemo_coqueiro_collation.tsv"

def n(pid):
    m=re.search(r"(\d+)$",pid)
    return int(m.group(1)) if m else None

def put(decisions, nums, status, target="", note=""):
    for x in nums:
        decisions[x]=(status,target,note)

decisions={}

# Human-reviewed unique documentary blocks.
put(decisions, range(1,184), "unique", "", "No strong HM textual correspondence; narrative continuity reviewed.")
put(decisions, range(190,224), "unique", "", "Coherent documentary block; no HM anchor >=0.70.")
put(decisions, range(257,275), "parallel_formulaic", "", "Formulaic/thematic HM parallels; not documentary equivalence.")

# Explicit human-reviewed correspondences and boundaries.
for pc,hm in [(184,146),(185,147),(186,148),(187,149),(188,150),(189,151),
              (224,146),(225,147),(226,148),(227,149),(228,150),(231,151),
              (252,176),(253,177),(255,140),(256,141),(275,137)]:
    decisions[pc]=("confirmed",f"BOR-CORBO-HM001-u{hm:03d}","Human-reviewed textual/narrative correspondence.")

# PC229-230 expand material around HM u150; do not force 1:1.
put(decisions,[229,230],"parallel_formulaic","BOR-CORBO-HM001-u150",
    "Expanded net episode around HM u150; no strict 1:1 equivalence.")
# Structural parallel only.
put(decisions,[240,241,242],"parallel_formulaic","",
    "Structural/formulaic parallel to HM u148-u151 with different referents; not textual equivalence.")

# Final human review of the formerly unresolved middle block.
# PC232-237 continue the fishing/net narrative, but segmentation diverges enough
# that no strict HM unit ID is forced here.
put(decisions, range(232,238), "parallel_formulaic", "",
    "Continuation of the confirmed net/fish episode; HM segmentation diverges, so no forced 1:1 match.")
# PC238-250 are the paca/apueceba episode: structurally parallel to the fish/net
# narrative, but with different referents and hunting technology.
put(decisions, range(238,251), "parallel_formulaic", "",
    "Paca/apueceba episode; structural/formulaic parallel, not textual equivalence.")
# PC251 introduces the queixada encounter; PC252-253 are confirmed below.
decisions[251]=("parallel_formulaic","",
    "Transition into queixada episode; thematic/structural HM parallel without strict equivalence.")
decisions[254]=("parallel_formulaic","",
    "Queixada description continues confirmed PC252-253 but differs materially from HM fish/net wording.")

# Late sequence: anchors and sequence-supported candidates established in review.
late={276:138,277:139,278:140,279:141,280:142,282:144,283:145,284:146,285:147,
286:148,287:149,288:150,289:151,290:152,291:153,292:154,293:155,294:156,
295:157,296:158,297:159,298:160,301:162,302:163,303:164,304:165,307:167,
308:168,309:169,310:170,311:171,312:172,313:173,314:174,315:175,316:176,
317:177,318:178,319:179,320:180,321:181,322:182,323:183,324:184,325:185,
330:190,331:191,332:192,333:193,334:194,335:195,336:196}
for pc,hm in late.items():
    decisions[pc]=("confirmed",f"BOR-CORBO-HM001-u{hm:03d}",
                   "Strong anchor or sequence-supported human-reviewed correspondence.")

with SRC.open(encoding="utf-8",newline="") as f:
    rows=list(csv.DictReader(f,delimiter="\t"))

fields=["id","status","corbo_match_id","decision_note"]
with OUT.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n")
    w.writeheader()
    for r in rows:
        x=n(r["id"])
        status,target,note=decisions.get(x,("unresolved","","Not yet resolved by human collation."))
        w.writerow({"id":r["id"],"status":status,"corbo_match_id":target,"decision_note":note})

from collections import Counter
counts=Counter()
for r in rows:
    x=n(r["id"])
    counts[decisions.get(x,("unresolved","",""))[0]]+=1
print(f"Gerado: {OUT.relative_to(ROOT)}")
print(f"Unidades: {len(rows)}")
for k in ("unique","confirmed","parallel_formulaic","unresolved"):
    print(f"{k}: {counts[k]}")
