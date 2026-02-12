# genai-poc1

FastAPI project with:
- OpenAI client wrapper (OpenAI.py)
- Wikipedia scraper endpoint (/scrape)
- Chat endpoint (feature1 history)

## Setup

1) Create a virtualenv (optional):
   python3 -m venv .venv && source .venv/bin/activate

2) Install deps:
   pip install -r requirements.txt

3) Configure environment (only needed for OpenAI):
   cp .env.example .env
   # edit .env and set OPENAI_API_KEY=sk-...

## Run

uvicorn main:app --reload --port 8000

## Use

- Scrape Generative AI page (default):
  curl -X POST http://localhost:8000/scrape \
    -H 'Content-Type: application/json' \
    -d '{"max_chars": 800}'

- Scrape custom title:
  curl -X POST http://localhost:8000/scrape \
    -H 'Content-Type: application/json' \
    -d '{"title":"Large language model","max_chars": 800}'

## Tests

- Dev deps: pip install -r requirements-dev.txt
- Run: pytest -q
