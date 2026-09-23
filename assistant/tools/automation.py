"""Keyboard, mouse, and screenshot automation via PyAutoGUI."""

from datetime import datetime
from pathlib import Path

from assistant.config import PROJECT_ROOT
from assistant.tools.paths import ensure_within_home, resolve_path

SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"


def _pyautogui():
    import pyautogui

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    return pyautogui


def type_text(text: str, interval: float = 0.02) -> dict[str, str]:
    """Type text into the currently focused window."""
    try:
        gui = _pyautogui()
        gui.write(text, interval=max(0.0, min(interval, 0.5)))
        return {"status": "success", "message": f"Typed {len(text)} character(s)."}
    except Exception as exc:  # noqa: BLE001 — surface automation failures cleanly
        return {"status": "error", "message": f"Failed to type text: {exc}"}


def press_hotkey(keys: str) -> dict[str, str]:
    """Press a keyboard shortcut. Keys are '+' separated, e.g. 'ctrl+c' or 'win+e'."""
    try:
        gui = _pyautogui()
        parts = [k.strip().lower() for k in keys.replace("-", "+").split("+") if k.strip()]
        if not parts:
            return {"status": "error", "message": "No keys provided."}
        if len(parts) == 1:
            gui.press(parts[0])
        else:
            gui.hotkey(*parts)
        return {"status": "success", "message": f"Pressed: {'+'.join(parts)}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to press keys: {exc}"}


def move_mouse(x: int, y: int, duration: float = 0.3) -> dict[str, str]:
    """Move the mouse cursor to screen coordinates."""
    try:
        gui = _pyautogui()
        width, height = gui.size()
        if not (0 <= x < width and 0 <= y < height):
            return {
                "status": "error",
                "message": f"Coordinates ({x}, {y}) outside screen {width}x{height}.",
            }
        gui.moveTo(x, y, duration=max(0.0, min(duration, 3.0)))
        return {"status": "success", "message": f"Moved mouse to ({x}, {y})."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to move mouse: {exc}"}


def click(x: int | None = None, y: int | None = None, button: str = "left") -> dict[str, str]:
    """Click the mouse. Optionally move to (x, y) first."""
    try:
        gui = _pyautogui()
        button = button.lower().strip()
        if button not in {"left", "right", "middle"}:
            return {"status": "error", "message": "button must be left, right, or middle."}

        if x is not None and y is not None:
            width, height = gui.size()
            if not (0 <= x < width and 0 <= y < height):
                return {
                    "status": "error",
                    "message": f"Coordinates ({x}, {y}) outside screen {width}x{height}.",
                }
            gui.click(x, y, button=button)
            return {"status": "success", "message": f"{button.capitalize()} clicked at ({x}, {y})."}

        gui.click(button=button)
        return {"status": "success", "message": f"{button.capitalize()} clicked at current position."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to click: {exc}"}


def take_screenshot(
    filename: str | None = None,
    location: str | None = None,
) -> dict[str, str]:
    """Capture the full screen and save a PNG."""
    try:
        gui = _pyautogui()
        if location:
            folder = ensure_within_home(resolve_path(location))
        else:
            folder = SCREENSHOTS_DIR
        folder.mkdir(parents=True, exist_ok=True)

        name = filename or f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        if not name.lower().endswith(".png"):
            name = f"{name}.png"

        path = ensure_within_home(folder / name) if location else (folder / name).resolve()
        image = gui.screenshot()
        image.save(path)
        return {"status": "success", "message": f"Screenshot saved: {path}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to take screenshot: {exc}"}


def get_screen_size() -> dict[str, str]:
    """Return the primary screen resolution."""
    try:
        gui = _pyautogui()
        width, height = gui.size()
        return {"status": "success", "message": f"Screen size: {width}x{height}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Failed to get screen size: {exc}"}
