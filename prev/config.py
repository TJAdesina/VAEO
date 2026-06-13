"""
config.py — Centralised configuration for VAEO.
"""

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
        "spitch_voice": "ebuka",
        "flag": "🇳🇬",
    },
    "Hausa": {
        "code": "ha",
        "gemini_lang": "Hausa",
        "spitch_voice": "aliyu",
        "flag": "🇳🇬",
    },
}

# gemini-2.5-flash-lite-preview-09-2025 was discontinued.
# Use the stable alias.
GEMINI_MODEL_PRIMARY  = "gemini-2.5-flash"   # fast, high availability
GEMINI_MODEL_FALLBACK = "gemini-3-flash-preview"   # used on 503 / overload only

GEMINI_MAX_RETRIES = 3

SPITCH_AUDIO_MIME = "audio/wav"

# Max conversation turns sent to the AI (1 turn = user msg + assistant msg).
# Older turns are dropped to keep token count and latency low.
HISTORY_LIMIT = 15  # → keeps up to 30 messages

# ---------------------------------------------------------------------------
# Static welcome messages — no API call, instant, reliable for demos.
# ---------------------------------------------------------------------------
WELCOME_MESSAGES: dict[str, str] = {
    "English": (
        "Hello! I'm your Agricultural Extension Officer. "
        "Tell me about a problem with your crops or farm and I'll help you figure out what's going on."
    ),
    "Yoruba": (
        "Ẹ káàbọ̀! Mo jẹ́ Olùfọwọ́sí Àgbẹ̀ rẹ. "
        "Sọ fún mi nípa ìṣòro tí o ní lórí àgbàdo rẹ tàbí oko rẹ, èmi yóò ràn ọ́ lọ́wọ́."
    ),
    "Igbo": (
        "Nnọọ! Abụ m onye ọrụ ọ́gụgụ ubi gị. "
        "Kọọ m ihe nsogbu dị n'ubi gị, m ga-enyere gị aka ịchọpụta ihe mere."
    ),
    "Hausa": (
        "Sannu! Ni ne Jami'in Aikin Noma naka. "
        "Ka gaya mini matsalar da ke faruwa a gonarka, zan taimake ka gano abin da ke faruwa."
    ),
}

# ISO 639-1 code → language name (used for advisory switch-button labels)
ISO_TO_LANGUAGE: dict[str, str] = {v["code"]: k for k, v in LANGUAGES.items()}
