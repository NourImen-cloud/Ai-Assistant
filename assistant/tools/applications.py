import os
import subprocess
import webbrowser
from typing import Any

WEB_APPLICATIONS: dict[str, str] = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "spotify": "https://open.spotify.com",
    "netflix": "https://www.netflix.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "discord": "https://discord.com/app",
    "maps": "https://maps.google.com",
}


def find_browser_executable(preferred: str = "chrome") -> str | None:
    """Find absolute path to Chrome or Edge on Windows."""
    chrome_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    edge_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    ]

    order = chrome_candidates + edge_candidates if preferred == "chrome" else edge_candidates + chrome_candidates
    for p in order:
        if os.path.isfile(p):
            return p
    return None


APPLICATIONS: dict[str, dict[str, Any]] = {
    "chrome": {
        "aliases": ["chrome", "google chrome", "browser", "navigateur"],
        "process_names": ["chrome.exe"],
    },
    "edge": {
        "aliases": ["edge", "microsoft edge", "msedge"],
        "process_names": ["msedge.exe"],
    },
    "vscode": {
        "aliases": ["vscode", "vs code", "visual studio code", "code"],
        "command": ["code"],
        "shell": True,
        "process_names": ["Code.exe"],
    },
    "calculator": {
        "aliases": ["calculator", "calc", "calculatrice"],
        "command": ["calc"],
        "shell": True,
        "process_names": ["CalculatorApp.exe", "Calculator.exe", "calc.exe"],
    },
    "file explorer": {
        "aliases": ["file explorer", "explorer", "files", "fichiers", "explorateur"],
        "command": ["explorer"],
        "shell": True,
        "process_names": [],
        "closable": False,
    },
    "terminal": {
        "aliases": ["terminal", "command prompt", "cmd", "powershell", "windows terminal", "invite de commandes"],
        "command": ["wt"],
        "fallback": ["cmd"],
        "shell": True,
        "process_names": ["WindowsTerminal.exe", "cmd.exe", "powershell.exe", "pwsh.exe"],
    },
    "notepad": {
        "aliases": ["notepad", "text editor", "bloc-notes", "bloc notes"],
        "command": ["notepad"],
        "shell": True,
        "process_names": ["notepad.exe"],
    },
}


def _normalize(name: str) -> str:
    return name.strip().lower()


def _resolve_application(name: str) -> dict[str, Any] | None:
    normalized = _normalize(name)
    for app in APPLICATIONS.values():
        if normalized in app["aliases"]:
            return app
    return None


def open_application(name: str) -> dict[str, str]:
    """Launch a known application, web application, or custom executable by name."""
    clean_name = _normalize(name)

    # 1. Check if the target is a popular web service (YouTube, ChatGPT, Gmail, Spotify, etc.)
    for web_key, url in WEB_APPLICATIONS.items():
        if web_key in clean_name:
            browser_exe = find_browser_executable("chrome")
            if browser_exe:
                try:
                    subprocess.Popen([browser_exe, url])
                    return {"status": "success", "message": f"Opened {web_key.title()} ({url}) in {os.path.basename(browser_exe)}."}
                except Exception:
                    pass
            webbrowser.open(url)
            return {"status": "success", "message": f"Opened {web_key.title()} ({url}) in default browser."}

    # 2. Check if the app is Chrome or Edge specifically
    if any(alias in clean_name for alias in ["chrome", "google chrome"]):
        chrome_exe = find_browser_executable("chrome")
        if chrome_exe:
            try:
                subprocess.Popen([chrome_exe])
                return {"status": "success", "message": f"Opened Google Chrome ({chrome_exe})."}
            except Exception as e:
                return {"status": "error", "message": f"Failed to start Chrome: {e}"}

    if any(alias in clean_name for alias in ["edge", "microsoft edge"]):
        edge_exe = find_browser_executable("edge")
        if edge_exe:
            try:
                subprocess.Popen([edge_exe])
                return {"status": "success", "message": f"Opened Microsoft Edge ({edge_exe})."}
            except Exception as e:
                return {"status": "error", "message": f"Failed to start Edge: {e}"}

    # 3. Check known registered desktop apps
    app = _resolve_application(name)
    if app and "command" in app:
        try:
            subprocess.Popen(app["command"], shell=app.get("shell", True))
            return {"status": "success", "message": f"Opened {name}."}
        except FileNotFoundError:
            fallback = app.get("fallback")
            if fallback:
                subprocess.Popen(fallback, shell=True)
                return {"status": "success", "message": f"Opened {name} (fallback)."}
            return {"status": "error", "message": f"Could not find {name} on this system."}
        except OSError as exc:
            return {"status": "error", "message": f"Failed to open {name}: {exc}"}

    # 4. Fallback: try Windows 'start' command with empty title parameter
    try:
        subprocess.Popen(["start", "", name], shell=True)
        return {"status": "success", "message": f"Launched application '{name}'."}
    except OSError as exc:
        return {"status": "error", "message": f"Failed to open {name}: {exc}"}


def close_application(name: str) -> dict[str, str]:
    """Close a known application by terminating its process(es)."""
    app = _resolve_application(name)
    if app is None:
        return {
            "status": "error",
            "message": (
                f"Unknown application '{name}'. "
                f"Closable apps: {', '.join(list_applications())}."
            ),
        }

    if app.get("closable") is False or not app.get("process_names"):
        return {
            "status": "error",
            "message": f"Closing '{name}' is not supported for safety reasons.",
        }

    closed_any = False
    errors: list[str] = []
    for process_name in app["process_names"]:
        try:
            result = subprocess.run(
                ["taskkill", "/IM", process_name, "/F"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                closed_any = True
            elif "not found" not in (result.stderr or "").lower():
                errors.append((result.stderr or result.stdout or "").strip())
        except OSError as exc:
            errors.append(str(exc))

    if closed_any:
        return {"status": "success", "message": f"Closed {name}."}

    if errors:
        return {"status": "error", "message": f"Failed to close {name}: {'; '.join(errors)}"}

    return {"status": "error", "message": f"{name} does not appear to be running."}


def list_applications() -> list[str]:
    """Return human-readable names of supported applications."""
    return sorted({app["aliases"][0] for app in APPLICATIONS.values()})
