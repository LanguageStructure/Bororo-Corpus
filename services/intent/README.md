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

`evaluation.json` contains the frozen `1.0-challenge` set: 30 cases (15 positive, 5 ambiguous, 10 boundary). Score AI interpretation, deterministic validation, and licensed subject realization separately. Transient transport failures are retried and reported separately. Never alter the frozen gold, parser instructions, or grammar merely to make a prediction pass; corrections require a new evaluation-set version and a documented reason.\n\nFirst complete frozen-set run (2026-10-03): 30/30 validator decisions, 20/20 explicit intent gold matches, and 16/16 subject-realization gold matches, with 0 transport failures. This is a controlled challenge-set result, not a general accuracy estimate.
