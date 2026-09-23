"""Browser automation via Playwright."""

from typing import Any
from urllib.parse import quote_plus, urlparse

_playwright = None
_browser = None
_context = None
_page = None


def _ensure_page():
    global _playwright, _browser, _context, _page
    if _page is not None and not _page.is_closed():
        return _page

    from playwright.sync_api import sync_playwright

    if _playwright is None:
        _playwright = sync_playwright().start()
    _browser = _playwright.chromium.launch(headless=False)
    _context = _browser.new_context()
    _page = _context.new_page()
    return _page


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty.")
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
    return url


def open_browser() -> dict[str, str]:
    try:
        _ensure_page()
        return {"status": "success", "message": "Browser opened."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to open browser: {exc}"}


def navigate(url: str) -> dict[str, str]:
    try:
        page = _ensure_page()
        normalized = _normalize_url(url)
        page.goto(normalized, wait_until="domcontentloaded", timeout=30000)
        return {"status": "success", "message": f"Navigated to {normalized}."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Navigation failed: {exc}"}


def search_google(query: str) -> dict[str, str]:
    try:
        page = _ensure_page()
        page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=30000)
        page.fill('textarea[name="q"], input[name="q"]', query)
        page.keyboard.press("Enter")
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        return {"status": "success", "message": f"Searched Google for '{query}'."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Google search failed: {exc}"}


def search_youtube(query: str) -> dict[str, str]:
    try:
        page = _ensure_page()
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return {"status": "success", "message": f"Searched YouTube for '{query}'."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"YouTube search failed: {exc}"}


def click_element(selector: str) -> dict[str, str]:
    try:
        page = _ensure_page()
        page.click(selector, timeout=10000)
        return {"status": "success", "message": f"Clicked element: {selector}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Click failed: {exc}"}


def type_into_field(selector: str, text: str) -> dict[str, str]:
    try:
        page = _ensure_page()
        page.fill(selector, text, timeout=10000)
        return {"status": "success", "message": f"Typed into {selector}."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Type failed: {exc}"}


def get_page_content(max_chars: int = 3000) -> dict[str, str]:
    try:
        page = _ensure_page()
        title = page.title()
        text = page.inner_text("body")
        text = " ".join(text.split())
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        return {
            "status": "success",
            "message": f"Title: {title}\n\n{text}",
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to read page: {exc}"}


def close_browser() -> dict[str, str]:
    global _playwright, _browser, _context, _page
    try:
        if _page and not _page.is_closed():
            _page.close()
        if _context:
            _context.close()
        if _browser:
            _browser.close()
        if _playwright:
            _playwright.stop()
        _page = _context = _browser = _playwright = None
        return {"status": "success", "message": "Browser closed."}
    except Exception as exc:  # noqa: BLE001
        _page = _context = _browser = _playwright = None
        return {"status": "error", "message": f"Failed to close browser: {exc}"}
