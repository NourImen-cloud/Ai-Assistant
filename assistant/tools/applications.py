import subprocess
from typing import Any

# Known applications with Windows launch commands.
# Aliases let the AI match natural language to the right app.
APPLICATIONS: dict[str, dict[str, Any]] = {
    "chrome": {
        "aliases": ["chrome", "google chrome", "browser"],
        "command": ["start", "chrome"],
        "shell": True,
        "process_names": ["chrome.exe"],
    },
    "vscode": {
        "aliases": ["vscode", "vs code", "visual studio code", "code"],
        "command": ["code"],
        "shell": True,
        "process_names": ["Code.exe"],
    },
    "calculator": {
        "aliases": ["calculator", "calc"],
        "command": ["calc"],
        "shell": True,
        "process_names": ["CalculatorApp.exe", "Calculator.exe", "calc.exe"],
    },
    "file explorer": {
        "aliases": ["file explorer", "explorer", "files"],
        "command": ["explorer"],
        "shell": True,
        # Do not kill explorer.exe — it hosts the Windows shell.
        "process_names": [],
        "closable": False,
    },
    "terminal": {
        "aliases": ["terminal", "command prompt", "cmd", "powershell", "windows terminal"],
        "command": ["wt"],
        "fallback": ["cmd"],
        "shell": True,
        "process_names": ["WindowsTerminal.exe", "cmd.exe", "powershell.exe", "pwsh.exe"],
    },
    "notepad": {
        "aliases": ["notepad", "text editor"],
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
    """Launch a known application or a custom executable by name."""
    app = _resolve_application(name)

    if app:
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

    # Allow opening arbitrary apps by name via Windows 'start' command.
    try:
        subprocess.Popen(["start", "", name], shell=True)
        return {"status": "success", "message": f"Attempted to open {name}."}
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
