"""Text-to-speech using pyttsx3 with automatic French / English voice selection."""

import pyttsx3

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate", 175)
    return _engine


def _select_voice_for_text(engine, text: str):
    """Automatically pick native French (Hortense) or English (Zira) voice."""
    french_words = {"bonjour", "voici", "merci", "tâches", "agenda", "votre", "pour", "dans", "avec", "est", "les", "des", "une", "que", "qui", "oui", "non"}
    words = set(text.lower().split())
    is_french = bool(words & french_words) or any(c in text for c in "éèàçêëîïôùû")

    try:
        voices = engine.getProperty("voices")
        for voice in voices:
            v_id = voice.id.lower()
            v_name = voice.name.lower()
            if is_french and ("fr-fr" in v_id or "french" in v_name or "hortense" in v_name):
                engine.setProperty("voice", voice.id)
                return
            elif not is_french and ("en-us" in v_id or "english" in v_name or "zira" in v_name):
                engine.setProperty("voice", voice.id)
                return
    except Exception:
        pass


def speak(text: str) -> dict[str, str]:
    """Speak text aloud through the system speakers with native language voice."""
    if not text.strip():
        return {"status": "error", "message": "Nothing to speak."}
    try:
        engine = _get_engine()
        _select_voice_for_text(engine, text)
        engine.say(text)
        engine.runAndWait()
        preview = text[:80] + ("..." if len(text) > 80 else "")
        return {"status": "success", "message": f"Spoke: {preview}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"TTS failed: {exc}"}
