import os
import subprocess
import webbrowser
from urllib.parse import urlparse

from assistant.tools.applications import _safe_popen, find_browser_executable


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty.")

    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"

    return url


def open_website(url: str) -> dict[str, str]:
    """Open a URL in the default browser."""
    try:
        normalized = _normalize_url(url)
        try:
            os.startfile(normalized)
        except Exception:
            webbrowser.open(normalized)
        return {"status": "success", "message": f"Opened {normalized}."}
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    except OSError as exc:
        return {"status": "error", "message": f"Failed to open website: {exc}"}


def open_website_in_chrome(url: str) -> dict[str, str]:
    """Open a URL specifically in Google Chrome (or system browser if Chrome is missing)."""
    try:
        normalized = _normalize_url(url)
        chrome_exe = find_browser_executable("chrome")
        if chrome_exe:
            try:
                os.startfile(chrome_exe, arguments=normalized)
                return {"status": "success", "message": f"Opened {normalized} in Google Chrome."}
            except Exception:
                try:
                    _safe_popen([chrome_exe, normalized])
                    return {"status": "success", "message": f"Opened {normalized} in Google Chrome."}
                except Exception:
                    pass

        # Fallback to default browser
        try:
            os.startfile(normalized)
        except Exception:
            webbrowser.open(normalized)
        return {"status": "success", "message": f"Opened {normalized} in default browser (Chrome not found)."}
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {"status": "error", "message": f"Failed to open website: {exc}"}
