import json, os, sys, urllib.request, urllib.error
from pathlib import Path

HERE=Path(__file__).resolve().parent
CASES=json.loads((HERE/"evaluation.json").read_text())
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
    # Evaluation-side checks only. The browser remains authoritative for exact
    # licensed morphology; this function tests states that are decidable from
    # the intent contract without reimplementing the grammar.
    if not intent or not intent.get("predicate"): return "NEEDS_CLARIFICATION"
    if intent["predicate"]!="maku": return "UNKNOWN_PREDICATE"
    s=intent.get("subject") or {}
    if s.get("Person")=="1" and s.get("Number")=="Plur" and s.get("Clusivity","_")=="_":
        return "NEEDS_CLARIFICATION"
    if not (intent.get("arguments") or {}).get("object"):
        return "UNLICENSED_FRAME"
    return "LICENSED"

rows=[]
for category,cases in CASES["categories"].items():
    for case in cases:
        row={"id":case["id"],"category":category,"input":case["input"]}
        try:
            intent=post(case["input"]); row["intent"]=intent
            row["intent_match"]=subset(case.get("expected_intent",{}),intent) if case.get("expected_intent") else None
            row["validator_observed"]=infer_validator(intent)
            row["validator_expected"]=case["expected_validator"]
            row["validator_match"]=row["validator_observed"]==row["validator_expected"]
        except Exception as e:
            row["error"]=str(e);row["intent_match"]=False;row["validator_match"]=False
        rows.append(row)

summary={
 "cases":len(rows),
 "endpoint":ENDPOINT,
 "intent_gold_cases":sum(r["intent_match"] is not None for r in rows),
 "intent_matches":sum(r["intent_match"] is True for r in rows),
 "validator_matches":sum(r["validator_match"] is True for r in rows)
}
report={"summary":summary,"results":rows}
out=HERE/"evaluation-results.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(summary,ensure_ascii=False,indent=2))
print("wrote",out)
