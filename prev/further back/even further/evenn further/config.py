"""
config.py — Centralised language and app configuration for VAEO.

Each language entry defines:
  - code         : ISO 639-1 code used by Spitch TTS
  - gemini_lang  : Human-readable name passed to Gemini STT prompt
  - spitch_voice : Voice identifier for Spitch TTS
  - flag         : Emoji flag for the UI
"""

# ---------------------------------------------------------------------------
# Language registry — add new languages here to extend the system.
# ---------------------------------------------------------------------------

LANGUAGES: dict[str, dict] = {
    "English": {
        "code": "en",
        "gemini_lang": "English",
        "spitch_voice": "john",
        "flag": "🇬🇧",
    },
    "Yoruba": {
        "code": "yo",
        "gemini_lang": "Yoruba",
        "spitch_voice": "femi",
        "flag": "🇳🇬",
    },
    "Igbo": {
        "code": "ig",
        "gemini_lang": "Igbo",
        "spitch_voice": "chidi",
        "flag": "🇳🇬",
    },
    "Hausa": {
        "code": "ha",
        "gemini_lang": "Hausa",
        "spitch_voice": "aminu",
        "flag": "🇳🇬",
    },
}

# Gemini model used for both STT and the diagnostic AI
GEMINI_MODEL = "gemini-3-flash-preview"

# Spitch TTS audio MIME type (Spitch always returns WAV)
SPITCH_AUDIO_MIME = "audio/wav"
