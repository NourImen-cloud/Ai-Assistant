import subprocess
import webbrowser
from urllib.parse import urlparse


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
        webbrowser.open(normalized)
        return {"status": "success", "message": f"Opened {normalized}."}
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    except OSError as exc:
        return {"status": "error", "message": f"Failed to open website: {exc}"}


def open_website_in_chrome(url: str) -> dict[str, str]:
    """Open a URL specifically in Google Chrome."""
    try:
        normalized = _normalize_url(url)
        subprocess.Popen(["start", "chrome", normalized], shell=True)
        return {"status": "success", "message": f"Opened {normalized} in Chrome."}
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    except OSError as exc:
        return {"status": "error", "message": f"Failed to open website in Chrome: {exc}"}
