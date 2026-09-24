"""Headless deep web research and synthesis tools — no browser, no CAPTCHA.

Uses DuckDuckGo (via `ddgs`) for search and `trafilatura` for high-quality
article extraction.  Falls back to BeautifulSoup if trafilatura cannot parse
the page.  All requests are plain HTTP — no Selenium/Playwright, so Google
CAPTCHAs are never triggered.
"""

import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Content extraction helpers
# ---------------------------------------------------------------------------

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _fetch_html(url: str, timeout: int = 8) -> str | None:
    """Download raw HTML from *url*. Returns ``None`` on failure."""
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def _extract_with_trafilatura(html: str, max_chars: int = 3000) -> str:
    """Use trafilatura for high-quality main-content extraction."""
    try:
        import trafilatura

        text = trafilatura.extract(html, include_comments=False, include_tables=False)
        if text:
            text = " ".join(text.split())
            return text[:max_chars]
    except Exception:
        pass
    return ""


def _extract_with_bs4(html: str, max_chars: int = 3000) -> str:
    """Fallback: strip boilerplate with BeautifulSoup."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
            tag.decompose()
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 40]
        full_text = " ".join(paragraphs)
        full_text = " ".join(full_text.split())
        return full_text[:max_chars]
    except Exception:
        return ""


def _fetch_clean_text(url: str, timeout: int = 8, max_chars: int = 500) -> str:
    """Fetch a URL and return cleaned article text (trafilatura → BS4 fallback)."""
    html = _fetch_html(url, timeout=timeout)
    if not html:
        return ""
    text = _extract_with_trafilatura(html, max_chars=max_chars)
    if text:
        return text
    return _extract_with_bs4(html, max_chars=max_chars)


def _fetch_page(entry: dict, timeout: int = 8, max_chars: int = 3000) -> dict:
    """Fetch deep content for one search result entry (used by thread pool)."""
    url = entry.get("url", "")
    page_text = _fetch_clean_text(url, timeout=timeout, max_chars=max_chars) if url else ""
    entry["content"] = page_text if page_text else entry.get("snippet", "")
    return entry


# ---------------------------------------------------------------------------
# DuckDuckGo search wrapper
# ---------------------------------------------------------------------------

def _ddg_search(query: str, max_results: int = 5) -> list[dict]:
    """Run a DuckDuckGo text search. Returns list of {title, url, snippet}."""
    try:
        from ddgs import DDGS
    except ImportError:
        # Legacy fallback
        from duckduckgo_search import DDGS  # type: ignore[no-redef]

    ddgs = DDGS()
    raw = list(ddgs.text(query, max_results=max_results))
    results = []
    for r in raw:
        results.append({
            "title": r.get("title", ""),
            "url": r.get("href") or r.get("link") or "",
            "snippet": r.get("body", ""),
        })
    return results


# ---------------------------------------------------------------------------
# Public tools
# ---------------------------------------------------------------------------

def deep_web_research(query: str, max_sources: int = 3) -> dict[str, Any]:
    """Perform headless web research on a query and extract key information with sources.

    This tool uses DuckDuckGo search + deep page fetching — **no browser
    window** is opened and **no CAPTCHA** will ever appear.
    """
    query = query.strip()
    if not query:
        return {"status": "error", "message": "Research query cannot be empty."}

    try:
        entries = _ddg_search(query, max_results=max_sources)
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Search failed ({exc}). Try again or rephrase the query.",
        }

    if not entries:
        return {"status": "success", "message": f"No results found for '{query}'."}

    # Fetch page content in parallel (much faster than sequential)
    with ThreadPoolExecutor(max_workers=min(len(entries), 5)) as pool:
        futures = {pool.submit(_fetch_page, e): e for e in entries}
        results = []
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception:
                results.append(futures[fut])

    # Sort back into original order
    url_order = {e["url"]: i for i, e in enumerate(entries)}
    results.sort(key=lambda r: url_order.get(r.get("url", ""), 999))

    sections = []
    for idx, r in enumerate(results, 1):
        content = r.get("content") or r.get("snippet", "(no content extracted)")
        sections.append(
            f"### Source {idx}: {r['title']}\n"
            f"**URL:** {r['url']}\n"
            f"**Key Info:** {content}\n"
        )

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


def academic_search(query: str, max_sources: int = 3) -> dict[str, Any]:
    """Search for academic papers and scholarly articles on a topic.

    Adds scholarly keywords to bias DuckDuckGo toward academic sites
    (arxiv, scholar, semantic scholar, PubMed, IEEE, ACM, etc.).
    """
    query = query.strip()
    if not query:
        return {"status": "error", "message": "Query cannot be empty."}

    scholarly_query = f"{query} site:arxiv.org OR site:scholar.google.com OR site:semanticscholar.org OR site:pubmed.ncbi.nlm.nih.gov"

    try:
        entries = _ddg_search(scholarly_query, max_results=max_sources)
    except Exception:
        # Fallback: try without site restriction
        try:
            entries = _ddg_search(f"{query} research paper arxiv", max_results=max_sources)
        except Exception as exc:
            return {"status": "error", "message": f"Academic search failed: {exc}"}

    if not entries:
        # Second fallback — plain query + "paper"
        try:
            entries = _ddg_search(f"{query} paper", max_results=max_sources)
        except Exception:
            pass

    if not entries:
        return {"status": "success", "message": f"No academic results found for '{query}'."}

    with ThreadPoolExecutor(max_workers=min(len(entries), 5)) as pool:
        futures = {pool.submit(_fetch_page, e, 10, 500): e for e in entries}
        results = []
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception:
                results.append(futures[fut])

    url_order = {e["url"]: i for i, e in enumerate(entries)}
    results.sort(key=lambda r: url_order.get(r.get("url", ""), 999))

    sections = []
    for idx, r in enumerate(results, 1):
        content = r.get("content") or r.get("snippet", "(no content extracted)")
        sections.append(
            f"### Paper {idx}: {r['title']}\n"
            f"**URL:** {r['url']}\n"
            f"**Abstract / Summary:** {content}\n"
        )

    return {
        "status": "success",
        "message": (
            f"Academic search for '{query}' — {len(results)} results:\n\n"
            + "\n".join(sections)
        ),
        "sources": results,
    }
