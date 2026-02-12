import os
from typing import List, Optional, Dict, Any

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

try:
    from openai import OpenAI as _OpenAI
except ImportError:  # pragma: no cover
    _OpenAI = None


class OpenAIClient:
    """Light wrapper around OpenAI Chat Completions.

    Usage:
        client = OpenAIClient()
        text = client.chat(prompt="Hello", system="Be concise")
    """

    def __init__(self, api_key: Optional[str] = None, default_model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set. Provide api_key or set env var.")
        if _OpenAI is None:
            raise RuntimeError("openai package not installed. pip install -r requirements.txt")
        self.client = _OpenAI(api_key=self.api_key)
        self.default_model = default_model

    def chat(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        messages: List[Dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""
