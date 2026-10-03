import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app, resources={r"/interpret": {"origins": "https://languagestructure.github.io"}})
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = os.environ.get("CORBO_INTENT_MODEL", "gpt-6-luna")

INTENT_SCHEMA = {
 "type":"object","additionalProperties":False,
 "properties":{
  "predicate":{"type":"string"},
  "construction":{"type":"string","enum":["basic","causative"]},
  "subject":{"type":"object","additionalProperties":False,"properties":{
   "Person":{"type":"string","enum":["1","2","3"]},
   "Number":{"type":"string","enum":["Sing","Plur"]},
   "Clusivity":{"type":"string","enum":["_","In","Ex"]}},
   "required":["Person","Number","Clusivity"]},
  "grammar":{"type":"object","additionalProperties":False,"properties":{
   "Mood":{"type":"string","enum":["_","Ind","Opt","Sub","Imp"]},
   "Aspect":{"type":"string","enum":["_","Prog"]},
   "Status":{"type":"string","enum":["_","Irr"]},
   "Polarity":{"type":"string","enum":["Pos","Neg"]},
   "Speech":{"type":"string","enum":["_","Ind","Quo"]},
   "VerbForm":{"type":"string","enum":["_","Ger"]},
   "Emph":{"type":"string","enum":["_","Yes"]}},
   "required":["Mood","Aspect","Status","Polarity","Speech","VerbForm","Emph"]},
  "arguments":{"type":"object","additionalProperties":False,"properties":{
   "object":{"type":["string","null"]},"complement":{"type":["string","null"]},"causee":{"anyOf":[{"type":"object","additionalProperties":False,"properties":{"Person":{"type":"string","enum":["1","2","3"]},"Number":{"type":"string","enum":["Sing","Plur"]}},"required":["Person","Number"]},{"type":"null"}]}},
   "required":["object","complement","causee"]}
 },
 "required":["predicate","construction","subject","grammar","arguments"]
}

INSTRUCTIONS = """You are only an intent parser for a controlled Bororo grammar.
Interpret Portuguese or English into the supplied grammatical JSON.
Do not generate Bororo words or sentences. Do not invent predicates.
Currently prefer predicate maku only when the input means 'dar/give'.
Use Irr for future/irrealis, Neg only for explicit negation, and distinguish
1PL inclusive/exclusive only when the input supplies enough information.
If the input is ambiguous, preserve conservative unmarked values; the downstream
deterministic validator decides whether clarification is required."""

@app.post("/interpret")
def interpret():
    body=request.get_json(silent=True) or {}
    text=(body.get("text") or "").strip()
    if not text:
        return jsonify(error="text must be non-empty"),400
    try:
        response=client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            input=text,
            text={"format":{"type":"json_schema","name":"corbo_intent","strict":True,"schema":INTENT_SCHEMA}}
        )
        return jsonify(intent=json.loads(response.output_text), model=MODEL)
    except Exception as exc:
        app.logger.exception("intent parsing failed")
        return jsonify(error="intent_parser_failed", detail=str(exc), model=MODEL), 502

@app.get("/health")
def health():
    return jsonify(ok=True, service="corbo-intent")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","8000")))
