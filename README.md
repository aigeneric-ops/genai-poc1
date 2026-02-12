# genai-poc1

FastAPI + OpenAI chat endpoint.

## Setup

1) Create a virtualenv (optional):
   python3 -m venv .venv && source .venv/bin/activate

2) Install deps:
   pip install -r requirements.txt

3) Configure environment:
   cp .env.example .env
   # edit .env and set OPENAI_API_KEY=sk-...

## Run

uvicorn main:app --reload --port 8000

## Test

curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Say hello from FastAPI","system":"Be concise","model":"gpt-4o-mini"}'
