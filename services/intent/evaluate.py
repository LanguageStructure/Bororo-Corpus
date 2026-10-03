import json, os, sys, urllib.request, urllib.error
from pathlib import Path

HERE=Path(__file__).resolve().parent
CASES=json.loads((HERE/"evaluation.json").read_text())
FRAMES=json.loads((HERE.parent.parent/"docs/data/generator-frames.json").read_text())
PREDICATES={p["lemma"]:p for p in FRAMES.get("predicates",[])}
SUBJECTS=FRAMES.get("subject_realizations",[])
CAUSEES=FRAMES.get("causee_realizations",[])
ENDPOINT=os.environ.get("CORBO_INTENT_ENDPOINT","https://bororo-corpus.onrender.com/interpret")

def post(text):
    data=json.dumps({"text":text,"language":"pt"}).encode()
    req=urllib.request.Request(ENDPOINT,data=data,headers={"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            return json.loads(r.read())["intent"]
    except urllib.error.HTTPError as e:
        body=e.read().decode("utf-8","replace")
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {body}") from e

def subset(expected,actual):
    if isinstance(expected,dict):
        return isinstance(actual,dict) and all(k in actual and subset(v,actual[k]) for k,v in expected.items())
    return expected==actual

def infer_validator(intent):
    # Mirrors the deterministic licensing conditions used by generator.html,
    # reading the same generator-frames.json rather than maintaining a second
    # hand-written inventory of licensed cells.
    if not intent: return "NEEDS_CLARIFICATION", None
    if intent.get("predicate_status")=="unknown": return "UNKNOWN_PREDICATE", None
    lemma=intent.get("predicate")
    if not lemma: return "NEEDS_CLARIFICATION", None
    pred=PREDICATES.get(lemma)
    if not pred: return "UNKNOWN_PREDICATE", None
    s=intent.get("subject") or {}; g=intent.get("grammar") or {}
    if not s.get("Person") or not s.get("Number"): return "NEEDS_CLARIFICATION", None
    if s.get("Person")=="1" and s.get("Number")=="Plur" and s.get("Clusivity","_")=="_":
        return "NEEDS_CLARIFICATION", None
    sel={"Person":str(s.get("Person")),"Number":s.get("Number"),"Clusivity":s.get("Clusivity") or "_",
         "Mood":g.get("Mood") or "_","Aspect":g.get("Aspect") or "_","Status":g.get("Status") or "_",
         "Polarity":g.get("Polarity") or "Pos","Speech":g.get("Speech") or "_",
         "Emph":g.get("Emph") or "_","VerbForm":g.get("VerbForm") or "_"}
    sr=next((x for x in SUBJECTS if all((x.get("selection") or {}).get(k,"_")==v for k,v in sel.items())),None)
    if not sr: return "UNLICENSED_COMBINATION", None
    args=intent.get("arguments") or {}
    if (intent.get("construction") or "basic")=="causative":
        cs=args.get("causee")
        if not cs: return "UNLICENSED_FRAME", None
        cr=next((x for x in CAUSEES if all(str((x.get("selection") or {}).get(k,"_"))==str(v) for k,v in cs.items())),None)
        if not cr: return "UNLICENSED_FRAME", None
    if "object" in pred.get("required",[]) and not args.get("object"): return "UNLICENSED_FRAME", None
    if pred.get("status")!="corpus-supported": return "UNLICENSED_FRAME", None
    return "LICENSED", sr.get("form")

rows=[]
for category,cases in CASES["categories"].items():
    for case in cases:
        row={"id":case["id"],"category":category,"input":case["input"]}
        try:
            intent=post(case["input"]); row["intent"]=intent
            row["intent_match"]=subset(case.get("expected_intent",{}),intent) if case.get("expected_intent") else None
            row["validator_observed"], row["subject_form_observed"]=infer_validator(intent)
            row["validator_expected"]=case["expected_validator"]
            row["validator_match"]=row["validator_observed"]==row["validator_expected"]
            row["subject_form_expected"]=case.get("expected_subject_form")
            row["subject_form_match"]=(row["subject_form_observed"]==row["subject_form_expected"]) if row["subject_form_expected"] else None
        except Exception as e:
            row["error"]=str(e);row["intent_match"]=False;row["validator_match"]=False;row["subject_form_match"]=False if case.get("expected_subject_form") else None
        rows.append(row)

summary={
 "cases":len(rows),
 "endpoint":ENDPOINT,
 "intent_gold_cases":sum(r["intent_match"] is not None for r in rows),
 "intent_matches":sum(r["intent_match"] is True for r in rows),
 "intent_mismatches":sum(r["intent_match"] is False for r in rows),
 "validator_matches":sum(r["validator_match"] is True for r in rows),
 "subject_form_gold_cases":sum(r.get("subject_form_match") is not None for r in rows),
 "subject_form_matches":sum(r.get("subject_form_match") is True for r in rows)
}
report={"summary":summary,"results":rows}
out=HERE/"evaluation-results.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(summary,ensure_ascii=False,indent=2))
print("wrote",out)
