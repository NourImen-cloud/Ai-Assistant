"""Echo Mind — Native Desktop Application Launcher.

Starts the unified backend and launches the UI in a dedicated,
borderless desktop application window using native Windows Edge/Chrome app mode.
"""

import os
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from assistant.config import API_HOST, API_PORT


def find_browser_app_executable() -> str | None:
    """Find Microsoft Edge or Google Chrome executable to run in native --app mode."""
    candidates = [
        # Microsoft Edge (present on all modern Windows 10/11)
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        # Google Chrome
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def run_backend_server():
    """Run uvicorn server in background thread."""
    import uvicorn
    from api.server import app

    uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="warning")


def wait_for_server(port: int, max_retries: int = 25) -> bool:
    """Wait until backend server is accepting connections."""
    url = f"http://127.0.0.1:{port}/health"
    for _ in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def main():
    # 1. Start backend server in a daemon thread
    server_thread = threading.Thread(target=run_backend_server, daemon=True)
    server_thread.start()

    # 2. Wait for server to become ready
    if not wait_for_server(API_PORT):
        print(f"Error: Backend server failed to start on port {API_PORT}")
        sys.exit(1)

    app_url = f"http://127.0.0.1:{API_PORT}"
    browser_exe = find_browser_app_executable()

    if browser_exe:
        # Launch dedicated borderless application window
        args = [
            browser_exe,
            f"--app={app_url}",
            "--window-size=1280,840",
            f"--user-data-dir={PROJECT_ROOT / 'data' / 'webview_profile'}",
        ]
        try:
            proc = subprocess.Popen(args)
            proc.wait()
            sys.exit(0)
        except Exception:
            webbrowser.open(app_url)
    else:
        # Fallback to standard default browser
        webbrowser.open(app_url)

    # Keep alive if fallback browser was used
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
