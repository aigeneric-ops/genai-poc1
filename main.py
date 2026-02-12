import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

import re
import httpx
from bs4 import BeautifulSoup  # type: ignore

app = FastAPI(title="genai-poc1 FastAPI (feature2)", version="0.2.0")

WIKI_BASE = "https://en.wikipedia.org"
DEFAULT_TITLE = "Generative_artificial_intelligence"  # "generative ai" page


class ScrapeRequest(BaseModel):
    title: Optional[str] = None  # Wikipedia page title, e.g., "Generative_artificial_intelligence"
    max_chars: int = 3000


class ScrapeResponse(BaseModel):
    title: str
    url: str
    content: str


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


def normalize_title(query: Optional[str]) -> str:
    if not query:
        return DEFAULT_TITLE
    # Replace spaces with underscores, preserve original casing except first char
    t = re.sub(r"\s+", "_", query.strip())
    # Only capitalize the very first character of the whole title (Wikipedia is case-sensitive beyond first char)
    if t:
        t = t[0:1].upper() + t[1:]
    return t


def extract_main_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#mw-content-text .mw-parser-output")
    if not content:
        return ""

    # Collect paragraphs and headings broadly (not just top-level) but avoid tables/infoboxes/navboxes
    blacklist = {"infobox", "vertical-navbox", "navbox", "metadata", "mbox"}
    parts = []
    for el in content.select("p, h2, h3"):
        # Skip if inside blacklisted containers
        skip = False
        for parent in el.parents:
            classes = parent.get("class") or []
            if any(cls in blacklist for cls in classes):
                skip = True
                break
            if parent.name in {"table", "figure", "aside"}:
                skip = True
                break
        if skip:
            continue
        text = el.get_text(" ", strip=True)
        if text:
            parts.append(text)

    text = "\n\n".join(parts)
    # Basic cleanup: remove reference markers like [1], [2]
    text = re.sub(r"\s*\[\d+\]", "", text)
    return text


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(req: ScrapeRequest) -> ScrapeResponse:
    title = normalize_title(req.title)
    url = f"{WIKI_BASE}/wiki/{title}"

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, headers={"User-Agent": "genai-poc1/0.2 (+fastapi)"})
            if r.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Wikipedia page not found: {title}")
            content = extract_main_content(r.text)
            if not content:
                raise HTTPException(status_code=500, detail="Failed to extract page content")
            if req.max_chars and len(content) > req.max_chars:
                content = content[: req.max_chars] + "…"
            return ScrapeResponse(title=title, url=url, content=content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Local dev: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
