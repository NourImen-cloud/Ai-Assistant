"""Headless deep web research and synthesis tools — no browser, no CAPTCHA.

Uses DuckDuckGo (via `ddgs`) for search and `trafilatura` for clean
article extraction.  Strictly bounded output size to fit within strict
free-tier LLM token limits (e.g. Groq 8000 TPM).
"""

import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_BLOCK_KEYWORDS = (
    "verify that you're not a robot",
    "enable javascript",
    "access denied",
    "just a moment...",
    "checking your browser",
    "security check",
    "captcha",
    "turn on javascript",
)


def _fetch_html(url: str, timeout: int = 6) -> str | None:
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def _is_blocked_or_junk(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in _BLOCK_KEYWORDS) or len(text.strip()) < 50


def _extract_with_trafilatura(html: str, max_chars: int = 400) -> str:
    try:
        import trafilatura

        text = trafilatura.extract(html, include_comments=False, include_tables=False)
        if text:
            cleaned = " ".join(text.split())
            if not _is_blocked_or_junk(cleaned):
                return cleaned[:max_chars]
    except Exception:
        pass
    return ""


def _extract_with_bs4(html: str, max_chars: int = 400) -> str:
    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
            tag.decompose()
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 40]
        full_text = " ".join(paragraphs)
        full_text = " ".join(full_text.split())
        if not _is_blocked_or_junk(full_text):
            return full_text[:max_chars]
    except Exception:
        pass
    return ""


def _fetch_clean_text(url: str, timeout: int = 6, max_chars: int = 400) -> str:
    html = _fetch_html(url, timeout=timeout)
    if not html:
        return ""
    text = _extract_with_trafilatura(html, max_chars=max_chars)
    if text:
        return text
    return _extract_with_bs4(html, max_chars=max_chars)


def _fetch_page(entry: dict, timeout: int = 6, max_chars: int = 400) -> dict:
    url = entry.get("url", "")
    page_text = _fetch_clean_text(url, timeout=timeout, max_chars=max_chars) if url else ""
    # If page extraction failed or was blocked, fall back to clean search snippet
    entry["content"] = page_text if page_text else (entry.get("snippet", "")[:max_chars])
    return entry


def _ddg_search(query: str, max_results: int = 3) -> list[dict]:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS  # type: ignore[no-redef]

    ddgs = DDGS()
    raw = list(ddgs.text(query, max_results=max_results))
    results = []
    for r in raw:
        url = r.get("href") or r.get("link") or ""
        # Skip generic homepages
        if url in {"https://scholar.google.com", "https://scholar.google.com/"}:
            continue
        results.append({
            "title": (r.get("title") or "")[:90],
            "url": url,
            "snippet": (r.get("body") or "")[:300],
        })
    return results[:max_results]


# ---------------------------------------------------------------------------
# Public tools
# ---------------------------------------------------------------------------

def deep_web_research(query: str, max_sources: int = 2) -> dict[str, Any]:
    """Perform fast, headless web research on any topic with key facts and sources."""
    query = query.strip()
    if not query:
        return {"status": "error", "message": "Research query cannot be empty."}

    max_sources = min(max(1, max_sources), 3)

    try:
        entries = _ddg_search(query, max_results=max_sources)
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Search failed ({exc}). Try again or rephrase.",
        }

    if not entries:
        return {"status": "success", "message": f"No web search results found for '{query}'."}

    with ThreadPoolExecutor(max_workers=min(len(entries), 3)) as pool:
        futures = {pool.submit(_fetch_page, e, 6, 400): e for e in entries}
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
        content = r.get("content") or r.get("snippet", "")
        sections.append(
            f"[{idx}] {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Summary: {content}"
        )

    return {
        "status": "success",
        "message": f"Research results for '{query}':\n\n" + "\n\n".join(sections),
        "sources": results,
    }


def compare_products_or_options(query: str, options: str = "") -> dict[str, Any]:
    """Conduct comparison research across multiple products, tools, or options."""
    full_query = f"{query} comparison {options}".strip()
    return deep_web_research(full_query, max_sources=2)


def academic_search(query: str, max_sources: int = 2) -> dict[str, Any]:
    """Search for academic papers and scholarly articles (arxiv, Scholar, etc.)."""
    query = query.strip()
    if not query:
        return {"status": "error", "message": "Query cannot be empty."}

    max_sources = min(max(1, max_sources), 3)
    scholarly_query = f"{query} site:arxiv.org OR site:semanticscholar.org OR research paper"

    try:
        entries = _ddg_search(scholarly_query, max_results=max_sources)
    except Exception:
        try:
            entries = _ddg_search(f"{query} arxiv research paper", max_results=max_sources)
        except Exception as exc:
            return {"status": "error", "message": f"Academic search failed: {exc}"}

    if not entries:
        try:
            entries = _ddg_search(f"{query} paper", max_results=max_sources)
        except Exception:
            pass

    if not entries:
        return {"status": "success", "message": f"No academic papers found for '{query}'."}

    with ThreadPoolExecutor(max_workers=min(len(entries), 3)) as pool:
        futures = {pool.submit(_fetch_page, e, 6, 400): e for e in entries}
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
        content = r.get("content") or r.get("snippet", "")
        sections.append(
            f"[Paper {idx}] {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Abstract: {content}"
        )

    return {
        "status": "success",
        "message": f"Academic papers for '{query}':\n\n" + "\n\n".join(sections),
        "sources": results,
    }
