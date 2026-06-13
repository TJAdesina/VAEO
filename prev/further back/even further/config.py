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

# ---------------------------------------------------------------------------
# Gemini model chain
#
# PRIMARY  — gemini-2.5-flash-lite:
#   Lighter weight → higher server availability → far fewer "high demand" 503s.
#   Fully multimodal (audio STT works perfectly). Faster too.
#
# FALLBACK — gemini-2.5-flash:
#   Automatically tried if flash-lite returns a capacity / overload error.
#   More powerful but more contested during peak hours.
#
# NOTE: gemini-2.0-flash was retired on 3 March 2026 — do NOT use.
# ---------------------------------------------------------------------------

GEMINI_MODEL_PRIMARY  = "gemini-3-flash-preview"  # fast, available
GEMINI_MODEL_FALLBACK = "gemini-3.5-flash"                      # used on 503 only

# Retry budget per API call (covers transient network drops + 503 spikes)
GEMINI_MAX_RETRIES = 3

# Spitch TTS audio MIME type (Spitch always returns WAV)
SPITCH_AUDIO_MIME = "audio/wav"
