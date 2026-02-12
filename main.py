import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Load .env if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# OpenAI SDK (>=1.0)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # Allows the app to start without the package (for CI/lint)

app = FastAPI(title="genai-poc1 FastAPI + OpenAI", version="0.1.1")


class ChatRequest(BaseModel):
    prompt: str
    system: Optional[str] = None
    model: Optional[str] = "gpt-4o-mini"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512


class ChatResponse(BaseModel):
    model: str
    output: str


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="openai package not installed. pip install -r requirements.txt")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set. Create a .env with OPENAI_API_KEY=... or export it in the environment.")

    try:
        client = OpenAI(api_key=api_key)

        # Compose messages for a standard Chat Completions call
        messages = []
        if req.system:
            messages.append({"role": "system", "content": req.system})
        messages.append({"role": "user", "content": req.prompt})

        completion = client.chat.completions.create(
            model=req.model or "gpt-4o-mini",
            messages=messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )

        output = completion.choices[0].message.content or ""
        return ChatResponse(model=req.model or "gpt-4o-mini", output=output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Local dev: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    # Lazy import to avoid uvicorn dependency at import time
    import uvicorn  # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
