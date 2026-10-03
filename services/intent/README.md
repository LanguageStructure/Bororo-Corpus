# CorBo intent service

Server-side AI layer for the controlled CorBo generator. It parses Portuguese/English into grammatical intent JSON. It does **not** generate Bororo.

Environment:
- `OPENAI_API_KEY` (required)
- `CORBO_INTENT_MODEL` (optional; default `gpt-6-luna`)
- `PORT` (optional)

Run:

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="..."
python app.py
```

The public generator should point `docs/data/generator-ai-config.json` to the deployed `/interpret` endpoint only after deployment and CORS configuration.

## Evaluation

`evaluation.json` separates positive, ambiguous, and boundary cases. Score the AI interpretation separately from the deterministic validator. Never expand the grammar merely to make an AI prediction pass.
