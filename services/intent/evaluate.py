import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

HERE=Path(__file__).resolve().parent
CASES=json.loads((HERE/"evaluation.json").read_text())
FRAMES=json.loads((HERE.parent.parent/"docs/data/generator-frames.json").read_text())
PREDICATES={p["lemma"]:p for p in FRAMES.get("predicates",[])}
SUBJECTS=FRAMES.get("subject_realizations",[])
CAUSEES=FRAMES.get("causee_realizations",[])
ENDPOINT=os.environ.get("CORBO_INTENT_ENDPOINT","https://bororo-corpus.onrender.com/interpret")

def post(text, max_attempts=3):
    data=json.dumps({"text":text,"language":"pt"}).encode()
    last_error=None
    for attempt in range(1,max_attempts+1):
        req=urllib.request.Request(ENDPOINT,data=data,headers={"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=60) as r:
                return json.loads(r.read())["intent"], attempt
        except urllib.error.HTTPError as e:
            body=e.read().decode("utf-8","replace")
            last_error=RuntimeError(f"HTTP {e.code} {e.reason}: {body[:500]}")
            if e.code not in (502,503,504) or attempt==max_attempts:
                raise last_error from e
            time.sleep(2*attempt)
        except (urllib.error.URLError, TimeoutError) as e:
            last_error=RuntimeError(f"transport error: {e}")
            if attempt==max_attempts:
                raise last_error from e
            time.sleep(2*attempt)
    raise last_error

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
            intent, attempts=post(case["input"]); row["intent"]=intent; row["transport_attempts"]=attempts
            row["intent_match"]=subset(case.get("expected_intent",{}),intent) if case.get("expected_intent") else None
            row["validator_observed"], row["subject_form_observed"]=infer_validator(intent)
            row["validator_expected"]=case["expected_validator"]
            row["validator_match"]=row["validator_observed"]==row["validator_expected"]
            row["subject_form_expected"]=case.get("expected_subject_form")
            row["subject_form_match"]=(row["subject_form_observed"]==row["subject_form_expected"]) if row["subject_form_expected"] else None
        except Exception as e:
            row["error"]=str(e);row["transport_failure"]=True;row["intent_match"]=None;row["validator_match"]=None;row["subject_form_match"]=None
        rows.append(row)

summary={
 "cases":len(rows),
 "endpoint":ENDPOINT,
 "intent_gold_cases":sum(r["intent_match"] is not None for r in rows),
 "intent_matches":sum(r["intent_match"] is True for r in rows),
 "intent_mismatches":sum(r["intent_match"] is False for r in rows),
 "transport_failures":sum(r.get("transport_failure") is True for r in rows),
 "evaluated_cases":sum(r.get("transport_failure") is not True for r in rows),
 "validator_matches":sum(r["validator_match"] is True for r in rows),
 "subject_form_gold_cases":sum(r.get("subject_form_match") is not None for r in rows),
 "subject_form_matches":sum(r.get("subject_form_match") is True for r in rows)
}
by_category={}
for category in CASES["categories"]:
    cr=[r for r in rows if r["category"]==category]
    by_category[category]={
      "cases":len(cr),
      "intent_gold_cases":sum(r["intent_match"] is not None for r in cr),
      "intent_matches":sum(r["intent_match"] is True for r in cr),
      "validator_matches":sum(r["validator_match"] is True for r in cr),
      "subject_form_gold_cases":sum(r.get("subject_form_match") is not None for r in cr),
      "subject_form_matches":sum(r.get("subject_form_match") is True for r in cr)
    }
failures=[{
  "id":r["id"],"category":r["category"],
  "intent_match":r.get("intent_match"),
  "validator_expected":r.get("validator_expected"),"validator_observed":r.get("validator_observed"),
  "subject_form_expected":r.get("subject_form_expected"),"subject_form_observed":r.get("subject_form_observed"),
  "error":r.get("error")
} for r in rows if r.get("intent_match") is False or r.get("validator_match") is False or r.get("subject_form_match") is False or r.get("transport_failure") is True]
report={"evaluation_set_version":CASES.get("version"),"frozen":CASES.get("challenge_set",{}).get("frozen",False),"summary":summary,"by_category":by_category,"failures":failures,"results":rows}
out=HERE/"evaluation-results.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"evaluation_set_version":CASES.get("version"),"frozen":CASES.get("challenge_set",{}).get("frozen",False),"summary":summary,"by_category":by_category,"failures":failures},ensure_ascii=False,indent=2))
print("wrote",out)
