import json
import os
import textwrap

import requests
import streamlit as st

st.set_page_config(page_title="Wiki Scraper UI", page_icon="📄", layout="centered")

st.title("📄 Wikipedia Scraper")

st.caption("Simple UI that calls the FastAPI /scrape endpoint in this repo.")

col1, col2 = st.columns([3, 1])
with col1:
    endpoint = st.text_input(
        "FastAPI endpoint",
        value=os.getenv("SCRAPER_ENDPOINT", "http://127.0.0.1:8123/scrape"),
        help="POST endpoint exposed by main.py (uvicorn main:app --port 8123)",
    )
with col2:
    max_chars = st.number_input("Max chars", min_value=200, max_value=10000, value=1200, step=100)

page_title = st.text_input(
    "Wikipedia title",
    value="Generative artificial intelligence",
    help="Example: Generative artificial intelligence (spaces OK)",
)

run = st.button("Scrape")

if run:
    try:
        payload = {"title": page_title, "max_chars": int(max_chars)}
        r = requests.post(endpoint, json=payload, timeout=20)
        if r.status_code != 200:
            st.error(f"Request failed: {r.status_code} — {r.text}")
        else:
            data = r.json()
            st.success("Scrape complete")
            st.write(f"Title: {data.get('title', '')}")
            url = data.get("url")
            if url:
                st.write(f"URL: {url}")
            content = data.get("content", "")
            st.text_area("Content", value=content, height=400)
            with st.expander("Raw JSON"):
                st.code(json.dumps(data, indent=2))
    except Exception as e:
        st.exception(e)

st.divider()

st.markdown(
    textwrap.dedent(
        """
        ### How to run
        1. Start the FastAPI server:
           ```bash
           uvicorn main:app --reload --port 8123
           ```
        2. Launch Streamlit UI:
           ```bash
           streamlit run streamlit_app.py
           ```
        """
    )
)
