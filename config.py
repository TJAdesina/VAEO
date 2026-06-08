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

# ---------------------------------------------------------------------------
# UI string translations — all static text rendered in app.py.
# Every key must exist for every language.
# ---------------------------------------------------------------------------
UI_STRINGS: dict[str, dict[str, str]] = {
    "English": {
        "page_title":           "🌱 VAEO — Agricultural Voice Assistant",
        "sidebar_header":       "⚙️ Settings",
        "sidebar_lang_label":   "🌍 Language",
        "sidebar_lang_help":    "Changes STT transcription, TTS voice, and AI response language.",
        "sidebar_new_chat":     "🗑️ New conversation",
        "sidebar_caption":      "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":      "🌱 Agricultural Voice Assistant",
        "page_subtitle":        "Type or speak your farming question.",
        "chat_input_placeholder": "Type your farming question…",
        "voice_section_header": "🎤 Voice Input",
        "voice_section_caption": "Click **Start Recording**, speak your question, then click **Stop Recording**.",
        "voice_start":          "▶ Start Recording",
        "voice_stop":           "⏹ Stop Recording",
        "spinner_transcribing": "Transcribing speech…",
        "spinner_switching":    "Switching language…",
        "spinner_tts":          "🔊 Generating voice…",
        "warn_inaudible":       "Could not understand the audio. Please speak clearly and try again.",
        "info_transcribed":     "📝 Transcribed",
        "err_transcription":    "⚠️ Transcription failed",
        "err_response":         "⚠️ Response error",
        "warn_voice_unavail":   "⚠️ Voice unavailable",
    },
    "Yoruba": {
        "page_title":           "🌱 VAEO — Olùrànlọ́wọ́ Ohùn Àgbẹ̀",
        "sidebar_header":       "⚙️ Ètò",
        "sidebar_lang_label":   "🌍 Èdè",
        "sidebar_lang_help":    "Yí ìtumọ̀ ọrọ̀, ohùn TTS, àti èdè ìdáhùn AI padà.",
        "sidebar_new_chat":     "🗑️ Ìjọ̀sọ̀ tuntun",
        "sidebar_caption":      "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":      "🌱 Olùrànlọ́wọ́ Ohùn Àgbẹ̀",
        "page_subtitle":        "Tẹ tàbí sọ ìbéèrè oko rẹ.",
        "chat_input_placeholder": "Tẹ ìbéèrè oko rẹ…",
        "voice_section_header": "🎤 Ohùn Tẹ̀dó",
        "voice_section_caption": "Tẹ **Bẹ̀rẹ̀ Gbigbasilẹ**, sọ ìbéèrè rẹ, lẹ́yìn náà tẹ **Dáwọ́ Gbigbasilẹ**.",
        "voice_start":          "▶ Bẹ̀rẹ̀ Gbigbasilẹ",
        "voice_stop":           "⏹ Dáwọ́ Gbigbasilẹ",
        "spinner_transcribing": "Ń ṣe ìtumọ̀ ọ̀rọ̀…",
        "spinner_switching":    "Ń yí èdè padà…",
        "spinner_tts":          "🔊 Ń ṣẹ̀dá ohùn…",
        "warn_inaudible":       "Kò lè gbọ́ ohun náà. Jọwọ́ sọ̀rọ̀ kedere kí o tún gbìyànjú.",
        "info_transcribed":     "📝 Ìtumọ̀",
        "err_transcription":    "⚠️ Ìtumọ̀ kùnà",
        "err_response":         "⚠️ Àṣìṣe ìdáhùn",
        "warn_voice_unavail":   "⚠️ Ohùn kò sí",
    },
    "Igbo": {
        "page_title":           "🌱 VAEO — Onye Enyemaka Ọ́gụgụ Ubi",
        "sidebar_header":       "⚙️ Ntọala",
        "sidebar_lang_label":   "🌍 Asụsụ",
        "sidebar_lang_help":    "Gbanwee ntụgharị olu, olu TTS, na asụsụ nzaghachi AI.",
        "sidebar_new_chat":     "🗑️ Mkparịta ụka ọhụrụ",
        "sidebar_caption":      "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":      "🌱 Onye Enyemaka Ọ́gụgụ Ubi",
        "page_subtitle":        "Pịnye ma ọ bụ kwuo ajụjụ ubi gị.",
        "chat_input_placeholder": "Pịnye ajụjụ ubi gị…",
        "voice_section_header": "🎤 Ntinye Olu",
        "voice_section_caption": "Pịa **Malite Ndekọ**, kwuo ajụjụ gị, wee pịa **Kwụsị Ndekọ**.",
        "voice_start":          "▶ Malite Ndekọ",
        "voice_stop":           "⏹ Kwụsị Ndekọ",
        "spinner_transcribing": "Na-atụgharị okwu…",
        "spinner_switching":    "Na-agbanwe asụsụ…",
        "spinner_tts":          "🔊 Na-emepụta olu…",
        "warn_inaudible":       "Enweghị ike ighọta ụda ahụ. Biko kwuo nkenke ma ọ bụ nke ọzọ.",
        "info_transcribed":     "📝 Atụgharịrị",
        "err_transcription":    "⚠️ Ntụgharị dara ada",
        "err_response":         "⚠️ Njehie nzaghachi",
        "warn_voice_unavail":   "⚠️ Olu adịghị",
    },
    "Hausa": {
        "page_title":           "🌱 VAEO — Mataimaki na Noma ta Murya",
        "sidebar_header":       "⚙️ Saitunan",
        "sidebar_lang_label":   "🌍 Harshe",
        "sidebar_lang_help":    "Canja rubutun magana, muryar TTS, da harshen amsar AI.",
        "sidebar_new_chat":     "🗑️ Sabon tattaunawa",
        "sidebar_caption":      "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":      "🌱 Mataimaki na Noma ta Murya",
        "page_subtitle":        "Rubuta ko faɗi tambayar noma ka.",
        "chat_input_placeholder": "Rubuta tambayar noma ka…",
        "voice_section_header": "🎤 Shigar Murya",
        "voice_section_caption": "Danna **Fara Rikodi**, faɗi tambayarka, sannan danna **Tsayar da Rikodi**.",
        "voice_start":          "▶ Fara Rikodi",
        "voice_stop":           "⏹ Tsayar da Rikodi",
        "spinner_transcribing": "Ana rubutun magana…",
        "spinner_switching":    "Ana canza harshe…",
        "spinner_tts":          "🔊 Ana samar da murya…",
        "warn_inaudible":       "Ba a fahimci sauti ba. Don Allah yi magana a fili ka sake gwadawa.",
        "info_transcribed":     "📝 An rubuta",
        "err_transcription":    "⚠️ Rubutun magana ya kasa",
        "err_response":         "⚠️ Kuskuren amsa",
        "warn_voice_unavail":   "⚠️ Murya ba ta samu ba",
    },
}
