"""Headless deep web research and synthesis tools without browser popups."""

import json
import urllib.request
from typing import Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup


def _fetch_clean_text(url: str, timeout: int = 5, max_chars: int = 1500) -> str:
    """Fetch and extract clean paragraph text from a URL."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            html = response.read().decode("utf-8", errors="replace")

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 40]
        full_text = " ".join(paragraphs)
        full_text = " ".join(full_text.split())
        return full_text[:max_chars]
    except Exception:
        return ""


def deep_web_research(query: str, max_sources: int = 3) -> dict[str, Any]:
    """Perform headless web research on a query and extract key information with sources."""
    query = query.strip()
    if not query:
        return {"status": "error", "message": "Research query cannot be empty."}

    results = []

    try:
        from duckduckgo_search import DDGS

        ddgs = DDGS()
        raw_results = list(ddgs.text(query, max_results=max_sources))
        for r in raw_results:
            url = r.get("href") or r.get("link") or ""
            title = r.get("title", "")
            snippet = r.get("body", "")

            # Attempt deep page fetch
            page_text = _fetch_clean_text(url, timeout=4, max_chars=1200) if url else ""
            summary_content = page_text if page_text else snippet

            results.append({
                "title": title,
                "url": url,
                "content": summary_content,
            })
    except Exception as exc:
        # Fallback to direct search URL query
        return {
            "status": "partial_success",
            "message": f"Web search service encountered an error ({exc}). You can open browser for '{query}'.",
        }

    if not results:
        return {"status": "success", "message": f"No web search results found for query: '{query}'."}

    sections = []
    for idx, r in enumerate(results, 1):
        sections.append(f"### Source {idx}: {r['title']}\n**URL:** {r['url']}\n**Key Info:** {r['content']}\n")

    return {
        "status": "success",
        "message": (
            f"Synthesized research for '{query}' from {len(results)} sources:\n\n"
            + "\n".join(sections)
        ),
        "sources": results,
    }


def compare_products_or_options(query: str, options: str = "") -> dict[str, Any]:
    """Conduct comparison research across multiple products, tools, or options."""
    full_query = f"{query} comparison {options}".strip()
    return deep_web_research(full_query, max_sources=3)
