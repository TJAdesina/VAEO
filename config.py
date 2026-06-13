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
    "Pidgin": {
        "code": "pcm",
        "gemini_lang": "Nigerian Pidgin",
        "spitch_voice": "jude",
        "spitch_code": "en",   # Spitch has no pcm locale; English voice pronounces Pidgin intelligibly
        "flag": "🇳🇬",
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

GEMINI_MODEL_PRIMARY  = "gemini-2.5-flash"        # fast, high availability
GEMINI_MODEL_FALLBACK = "gemini-3-flash-preview"  # used on 503 / overload only

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
    "Pidgin": (
        "How you dey! I be your Agricultural Extension Officer. "
        "Tell me wetin dey happen for your farm or your crops, I go help you find out wetin dey do am."
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

# ISO 639-1 / BCP-47 code → language name (used for advisory switch-button labels)
ISO_TO_LANGUAGE: dict[str, str] = {v["code"]: k for k, v in LANGUAGES.items()}

# ---------------------------------------------------------------------------
# UI string translations — all static text rendered in app.py / frontend.
# Every key must exist for every language.
# ---------------------------------------------------------------------------
UI_STRINGS: dict[str, dict[str, str]] = {
    "English": {
        "page_title":             "🌱 VAEO — Agricultural Voice Assistant",
        "sidebar_header":         "⚙️ Settings",
        "sidebar_lang_label":     "🌍 Language",
        "sidebar_lang_help":      "Changes STT transcription, TTS voice, and AI response language.",
        "sidebar_new_chat":       "New conversation",
        "sidebar_caption":        "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":        "🌱 Agricultural Voice Assistant",
        "page_subtitle":          "Type or speak your farming question.",
        "chat_input_placeholder": "Type your farming question…",
        "voice_section_header":   "🎤 Voice Input",
        "voice_section_caption":  "Press and hold to talk.",
        "voice_start":            "Hold to talk",
        "voice_stop":             "Release to send",
        "spinner_transcribing":   "Understanding…",
        "spinner_switching":      "Switching language…",
        "spinner_tts":            "🔊 Generating voice…",
        "warn_inaudible":         "Could not hear you. Please speak clearly and try again.",
        "info_transcribed":       "📝 Transcribed",
        "err_transcription":      "Transcription failed",
        "err_response":           "Response error",
        "warn_voice_unavail":     "Voice unavailable",
        "greeting":               "Good day, farmer.",
        "topic_crops":            "Crops",
        "topic_pests":            "Pests",
        "topic_soil":             "Soil",
        "topic_livestock":        "Livestock",
        "listening":              "Listening…",
        "understanding":          "Understanding…",
        "offline":                "You're offline. Messages will send when you reconnect.",
        "switch_to":              "Switch to",
    },
    "Pidgin": {
        "page_title":             "🌱 VAEO — Agric Voice Helper",
        "sidebar_header":         "⚙️ Settings",
        "sidebar_lang_label":     "🌍 Language",
        "sidebar_lang_help":      "E go change how e dey hear you, talk back, and respond.",
        "sidebar_new_chat":       "Start new talk",
        "sidebar_caption":        "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":        "🌱 Agric Voice Helper",
        "page_subtitle":          "Type or talk your farm question.",
        "chat_input_placeholder": "Type your farm question…",
        "voice_section_header":   "🎤 Talk Am",
        "voice_section_caption":  "Press and hold to talk.",
        "voice_start":            "Hold to talk",
        "voice_stop":             "Leave am to send",
        "spinner_transcribing":   "E dey hear you…",
        "spinner_switching":      "E dey change language…",
        "spinner_tts":            "🔊 E dey form voice…",
        "warn_inaudible":         "E no hear you well. Talk clear, try again.",
        "info_transcribed":       "📝 Wetin e hear",
        "err_transcription":      "E no fit hear you",
        "err_response":           "Wahala with answer",
        "warn_voice_unavail":     "Voice no dey work",
        "greeting":               "How you dey, farmer.",
        "topic_crops":            "Crops",
        "topic_pests":            "Pests",
        "topic_soil":             "Soil",
        "topic_livestock":        "Animals",
        "listening":              "E dey hear you…",
        "understanding":          "E dey understand…",
        "offline":                "No network. E go send when you get connection.",
        "switch_to":              "Switch to",
    },
    "Yoruba": {
        "page_title":             "🌱 VAEO — Olùrànlọ́wọ́ Ohùn Àgbẹ̀",
        "sidebar_header":         "⚙️ Ètò",
        "sidebar_lang_label":     "🌍 Èdè",
        "sidebar_lang_help":      "Yí ìtumọ̀ ọrọ̀, ohùn TTS, àti èdè ìdáhùn AI padà.",
        "sidebar_new_chat":       "Ìjọ̀sọ̀ tuntun",
        "sidebar_caption":        "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":        "🌱 Olùrànlọ́wọ́ Ohùn Àgbẹ̀",
        "page_subtitle":          "Tẹ tàbí sọ ìbéèrè oko rẹ.",
        "chat_input_placeholder": "Tẹ ìbéèrè oko rẹ…",
        "voice_section_header":   "🎤 Ohùn Tẹ̀dó",
        "voice_section_caption":  "Tẹ kí o sì dìmú láti sọ̀rọ̀.",
        "voice_start":            "Dìmú láti sọ̀rọ̀",
        "voice_stop":             "Tú sílẹ̀ láti firanṣẹ́",
        "spinner_transcribing":   "Ń gbọ́ ọ…",
        "spinner_switching":      "Ń yí èdè padà…",
        "spinner_tts":            "🔊 Ń ṣẹ̀dá ohùn…",
        "warn_inaudible":         "Kò gbọ́ ohun rẹ. Jọwọ́ sọ̀rọ̀ kedere kí o tún gbìyànjú.",
        "info_transcribed":       "📝 Ìtumọ̀",
        "err_transcription":      "Ìtumọ̀ kùnà",
        "err_response":           "Àṣìṣe ìdáhùn",
        "warn_voice_unavail":     "Ohùn kò sí",
        "greeting":               "Ẹ kú ọjọ́, àgbẹ̀.",
        "topic_crops":            "Irúgbìn",
        "topic_pests":            "Kòkòrò",
        "topic_soil":             "Ilẹ̀",
        "topic_livestock":        "Ẹran",
        "listening":              "Mo ń gbọ́…",
        "understanding":          "Ń gbọ́ ọ…",
        "offline":                "O kò sí lórí Íńtánẹ́ẹ̀tì.",
        "switch_to":              "Yí padà sí",
    },
    "Igbo": {
        "page_title":             "🌱 VAEO — Onye Enyemaka Ọ́gụgụ Ubi",
        "sidebar_header":         "⚙️ Ntọala",
        "sidebar_lang_label":     "🌍 Asụsụ",
        "sidebar_lang_help":      "Gbanwee ntụgharị olu, olu TTS, na asụsụ nzaghachi AI.",
        "sidebar_new_chat":       "Mkparịta ụka ọhụrụ",
        "sidebar_caption":        "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":        "🌱 Onye Enyemaka Ọ́gụgụ Ubi",
        "page_subtitle":          "Pịnye ma ọ bụ kwuo ajụjụ ubi gị.",
        "chat_input_placeholder": "Pịnye ajụjụ ubi gị…",
        "voice_section_header":   "🎤 Ntinye Olu",
        "voice_section_caption":  "Pịa ma jide iji kwuo.",
        "voice_start":            "Jide iji kwuo",
        "voice_stop":             "Hapụ iji zipu",
        "spinner_transcribing":   "Ana m anụ gị…",
        "spinner_switching":      "Na-agbanwe asụsụ…",
        "spinner_tts":            "🔊 Na-emepụta olu…",
        "warn_inaudible":         "Enweghị ike ighọta ụda ahụ. Biko kwuo nke ọma ma ọ bụ nke ọzọ.",
        "info_transcribed":       "📝 Atụgharịrị",
        "err_transcription":      "Ntụgharị dara ada",
        "err_response":           "Njehie nzaghachi",
        "warn_voice_unavail":     "Olu adịghị",
        "greeting":               "Ụbọchị ọma, onye ọrụ ubi.",
        "topic_crops":            "Ihe ọkụkụ",
        "topic_pests":            "Ụmụ ahụhụ",
        "topic_soil":             "Ala",
        "topic_livestock":        "Anụ ụlọ",
        "listening":              "Ana m ege ntị…",
        "understanding":          "Ana m anụ gị…",
        "offline":                "Ị nweghị Intanet.",
        "switch_to":              "Gbanwee gaa",
    },
    "Hausa": {
        "page_title":             "🌱 VAEO — Mataimaki na Noma ta Murya",
        "sidebar_header":         "⚙️ Saitunan",
        "sidebar_lang_label":     "🌍 Harshe",
        "sidebar_lang_help":      "Canja rubutun magana, muryar TTS, da harshen amsar AI.",
        "sidebar_new_chat":       "Sabon tattaunawa",
        "sidebar_caption":        "VAEO · Gemini 2.5 Flash · Spitch",
        "page_main_title":        "🌱 Mataimaki na Noma ta Murya",
        "page_subtitle":          "Rubuta ko faɗi tambayar noma ka.",
        "chat_input_placeholder": "Rubuta tambayar noma ka…",
        "voice_section_header":   "🎤 Shigar Murya",
        "voice_section_caption":  "Danna ka riƙe don magana.",
        "voice_start":            "Riƙe don magana",
        "voice_stop":             "Saki don aikawa",
        "spinner_transcribing":   "Ina jin ka…",
        "spinner_switching":      "Ana canza harshe…",
        "spinner_tts":            "🔊 Ana samar da murya…",
        "warn_inaudible":         "Ban ji ka ba. Don Allah yi magana a fili ka sake gwadawa.",
        "info_transcribed":       "📝 An rubuta",
        "err_transcription":      "Rubutun magana ya kasa",
        "err_response":           "Kuskuren amsa",
        "warn_voice_unavail":     "Murya ba ta samu ba",
        "greeting":               "Barka da rana, manomi.",
        "topic_crops":            "Amfanin gona",
        "topic_pests":            "Kwari",
        "topic_soil":             "Ƙasa",
        "topic_livestock":        "Dabbobi",
        "listening":              "Ina jin ka…",
        "understanding":          "Ina jin ka…",
        "offline":                "Babu Intanet.",
        "switch_to":              "Canja zuwa",
    },
}
