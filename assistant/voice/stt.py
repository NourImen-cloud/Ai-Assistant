"""High-speed Speech-to-text using Groq Whisper Turbo with Google STT fallback."""

import io
import speech_recognition as sr

from assistant.config import GROQ_API_KEY
from assistant.llm import create_client


def listen(timeout: float = 5.0, phrase_limit: float = 10.0) -> dict[str, str]:
    """Listen from default mic and return transcribed text with sub-second latency."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            # Low latency calibration (0.15s instead of 0.5s)
            recognizer.adjust_for_ambient_noise(source, duration=0.15)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
    except sr.WaitTimeoutError:
        return {"status": "error", "message": "No speech detected (timeout)."}
    except OSError as exc:
        return {"status": "error", "message": f"Microphone error: {exc}"}

    text = ""

    # Priority 1: High-Speed Groq Whisper Turbo (~150ms transcription)
    if GROQ_API_KEY:
        try:
            client = create_client()
            wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
            res = client.audio.transcriptions.create(
                file=("audio.wav", wav_bytes, "audio/wav"),
                model="whisper-large-v3-turbo",
            )
            text = (res.text or "").strip()
            if text:
                return {"status": "success", "message": text, "text": text}
        except Exception:
            # Fall through to Google STT fallback
            pass

    # Priority 2: Google Speech Recognition fallback
    try:
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return {"status": "error", "message": "Could not understand audio."}
    except sr.RequestError:
        try:
            text = recognizer.recognize_sphinx(audio)
        except (sr.UnknownValueError, sr.RequestError, OSError):
            return {
                "status": "error",
                "message": "Speech recognition unavailable. Check internet or install pocketsphinx.",
            }
    except Exception as exc:
        return {"status": "error", "message": f"Speech recognition error: {exc}"}

    text = (text or "").strip()
    if not text:
        return {"status": "error", "message": "Empty transcription."}
    return {"status": "success", "message": text, "text": text}
