# Kira AI Support Assistant — RAG Service

A small, production-structured RAG service that answers questions using only
`data/kb.json`, refuses off-topic questions, and is deployable as an HTTP API.

## What changed from the prototype (audit summary)

| Issue in prototype | Fix |
|---|---|
| KB loaded via `exec()` on a `.py` file (code execution risk) | KB is now plain JSON, loaded with `json.load` — no code execution |
| Recomputed embeddings every start | Embeddings cached to disk (`.cache/`), auto-invalidated when KB content changes |
| No error handling around the LLM call | Retries + automatic fallback model (70B → 8B) on rate limit/timeout/API error |
| Answers could ramble | System prompt caps replies at 2–4 sentences; `max_tokens` lowered to 180 |
| No input validation | Empty/oversized/control-character input rejected before it reaches the model |
| CLI-only | FastAPI HTTP service with `/ask` and `/health` endpoints |
| No rate limiting | Per-IP sliding-window limiter (default: 20 req/min) |
| No logging | Structured logs for every answer/refusal, with score + latency |
| No tests | `tests/` covers guardrails and KB loading |
| Not containerized | `Dockerfile` included, pre-downloads the embedding model at build time |

## Project structure

```
app/
  config.py       # all settings, from env vars
  kb_loader.py     # safe JSON KB loading + validation
  retriever.py     # embeddings + cosine similarity, disk-cached
  guardrails.py     # input validation + relevance gate
  llm.py           # Groq calls with retry/fallback
  service.py        # orchestrates the above
  main.py           # FastAPI app
cli.py               # local terminal testing, no server needed
data/kb.json          # your knowledge base
scripts/convert_kb.py  # one-time migration from old kb.py format
tests/                 # pytest suite
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then edit .env and add your GROQ_API_KEY
```

## Run locally (CLI, fastest way to test)

```bash
python cli.py
```

## Run as a web service

```bash
uvicorn app.main:app --reload --port 8000
```

Then:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "how do I reset my password?"}'

curl http://localhost:8000/health
```

## Run tests

```bash
pytest
```

## Deploy with Docker

```bash
docker build -t kira-rag .
docker run -p 8000:8000 --env-file .env kira-rag
```

## Tuning

- `RELEVANCE_THRESHOLD` (default 0.30): raise it to refuse more aggressively,
  lower it if it's refusing questions it shouldn't.
- `TOP_K` (default 4): how many KB entries get fed to the LLM as context.
- `MAX_ANSWER_TOKENS` (default 180): hard cap on answer length.

## Before going fully live — things this build does NOT cover yet

- **Auth**: `/ask` is open to anyone who can reach it. Add an API key or auth
  layer before exposing it publicly.
- **Multi-instance rate limiting**: the current limiter is in-memory per
  process. If you run more than one server instance, swap it for a
  Redis-backed limiter.
- **CORS**: currently `allow_origins=["*"]` — restrict to your real frontend
  domain in `app/main.py` before production.
- **Monitoring/alerting**: logs are structured but not shipped anywhere.
  Wire them to your logging stack (e.g. CloudWatch, Datadog) in production.
