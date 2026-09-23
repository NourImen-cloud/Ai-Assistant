"""Text-to-speech using pyttsx3 (local, free)."""

import pyttsx3

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate", 175)
    return _engine


def speak(text: str) -> dict[str, str]:
    """Speak text aloud through the system speakers."""
    if not text.strip():
        return {"status": "error", "message": "Nothing to speak."}
    try:
        engine = _get_engine()
        engine.say(text)
        engine.runAndWait()
        preview = text[:80] + ("..." if len(text) > 80 else "")
        return {"status": "success", "message": f"Spoke: {preview}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"TTS failed: {exc}"}
