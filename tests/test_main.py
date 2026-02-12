import pytest
import re
from fastapi.testclient import TestClient

from main import app, normalize_title, extract_main_content


client = TestClient(app)


def test_normalize_title_defaults():
    assert normalize_title(None) == "Generative_artificial_intelligence"


def test_normalize_title_spacing_and_case():
    assert normalize_title("generative ai") == "Generative_ai"
    assert normalize_title("Generative artificial intelligence") == "Generative_artificial_intelligence"


def test_extract_main_content_basic():
    html = '''
    <div id="mw-content-text">
      <div class="mw-parser-output">
        <p>Para 1 with ref [1].</p>
        <h2>Heading</h2>
        <p>Para 2</p>
        <table><tr><td>Ignore tables</td></tr></table>
      </div>
    </div>
    '''
    text = extract_main_content(html)
    # Should include paragraphs and headings, remove [1]
    assert "Para 1 with ref" in text and "[1]" not in text
    assert "Heading" in text
    assert "Ignore tables" not in text


def test_scrape_integration_live_wiki_smoke():
    # Smoke test hitting Wikipedia; if network is unavailable, skip
    try:
        r = client.post("/scrape", json={"title": "Generative artificial intelligence", "max_chars": 500})
    except Exception:
        pytest.skip("Network not available for live Wikipedia smoke test")
    assert r.status_code == 200
    data = r.json()
    assert data["title"].startswith("Generative_")
    assert data["url"].startswith("https://en.wikipedia.org/wiki/")
    assert isinstance(data["content"], str) and len(data["content"]) <= 505
