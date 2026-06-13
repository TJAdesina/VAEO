"""
app.py — VAEO: Virtual Agricultural Extension Officer
        A multilingual voice-interactive AI assistant for Nigerian farmers.

Architecture at a glance
─────────────────────────
  config.py          → language registry + model constants
  diagnostic_system.py → Gemini-powered AEO brain (text in / text out)
  stt.py             → Gemini STT  (audio bytes → transcribed text)
  tts.py             → Spitch TTS  (text → WAV bytes)
  app.py  (this file) → Streamlit UI, state management, orchestration

Run command
───────────
  streamlit run app.py
"""

import base64
import logging

import streamlit as st
from streamlit_mic_recorder import mic_recorder

from config import LANGUAGES, SPITCH_AUDIO_MIME
from diagnostic_system import process_user_message
from stt import transcribe_audio
from tts import synthesize_speech

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="🌱 VAEO — Agricultural Voice Assistant",
    page_icon="🌱",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Session state initialisation (runs only once per browser session)
# ---------------------------------------------------------------------------

def _init_state() -> None:
    defaults = {
        "history": [],            # list[dict] — full conversation history
        "language": "English",    # currently selected language
        "tts_queue": None,        # WAV bytes waiting to be played
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

_init_state()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _autoplay_audio(wav_bytes: bytes) -> None:
    """Inject an HTML <audio autoplay> tag so TTS plays without a button."""
    b64 = base64.b64encode(wav_bytes).decode()
    html = (
        f'<audio autoplay style="display:none">'
        f'<source src="data:audio/wav;base64,{b64}" type="audio/wav">'
        f"</audio>"
    )
    st.markdown(html, unsafe_allow_html=True)


def _render_history() -> None:
    """Render the full conversation history in the chat window."""
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


def _handle_input(user_text: str) -> None:
    """
    Central pipeline for any user input (text or transcribed voice):
      1. Validate
      2. Show user message immediately
      3. Call the AI brain
      4. Show assistant response immediately
      5. Generate TTS asynchronously and store in session state
    """
    user_text = user_text.strip()
    if not user_text:
        return

    # --- 1. Append user turn to history and render it ---
    st.session_state.history.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    # --- 2. Get AI response ---
    with st.spinner("Thinking..."):
        try:
            ai_response, updated_history = process_user_message(
                user_text,
                # Pass history WITHOUT the user turn we just appended;
                # process_user_message re-appends it internally.
                st.session_state.history[:-1],
            )
            st.session_state.history = updated_history
            assistant_text: str = ai_response.get("content", "")
        except Exception as exc:
            logger.error("AI error: %s", exc, exc_info=True)
            st.error(f"⚠️ Assistant error: {exc}")
            return

    # --- 3. Show assistant response immediately ---
    with st.chat_message("assistant"):
        st.write(assistant_text)

    # --- 4. Generate TTS and queue it for playback ---
    # with st.spinner("Generating voice response..."):
    #     try:
    #         wav_bytes = synthesize_speech(
    #             assistant_text,
    #             st.session_state.language,
    #         )
    #         st.session_state.tts_queue = wav_bytes
    #     except Exception as exc:
    #         logger.warning("TTS failed (non-fatal): %s", exc)
    #         st.warning(f"⚠️ Voice response unavailable: {exc}")


# ---------------------------------------------------------------------------
# Sidebar — language selector
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    lang_names = list(LANGUAGES.keys())
    selected = st.selectbox(
        "🌍 Conversation language",
        options=lang_names,
        index=lang_names.index(st.session_state.language),
        format_func=lambda name: (
            f"{LANGUAGES[name]['flag']} {name}"
        ),
        help="Sets the language for voice recognition, TTS playback, and AI responses.",
    )

    if selected != st.session_state.language:
        st.session_state.language = selected
        st.success(f"Language changed to {selected}.")

    st.markdown("---")

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.tts_queue = None
        st.rerun()

    st.markdown("---")
    st.caption(
        "**VAEO** — Virtual Agricultural Extension Officer  \n"
        "Powered by Gemini 2.5 Flash & Spitch"
    )

# ---------------------------------------------------------------------------
# Main page — title + intro
# ---------------------------------------------------------------------------

st.title("🌱 Agricultural Voice Assistant")
st.caption(
    f"Speaking **{st.session_state.language}** "
    f"{LANGUAGES[st.session_state.language]['flag']}  •  "
    "Type or record your farming question below."
)

# ---------------------------------------------------------------------------
# Conversation display
# ---------------------------------------------------------------------------

_render_history()

# ---------------------------------------------------------------------------
# Auto-play TTS if audio is queued (runs after every rerun)
# ---------------------------------------------------------------------------

if st.session_state.tts_queue:
    _autoplay_audio(st.session_state.tts_queue)
    st.session_state.tts_queue = None   # consume once

# ---------------------------------------------------------------------------
# Text input (st.chat_input stays anchored to the bottom of the page)
# ---------------------------------------------------------------------------

text_input = st.chat_input("Type your farming question here…")
if text_input:
    _handle_input(text_input)
    st.rerun()

# ---------------------------------------------------------------------------
# Voice input
# ---------------------------------------------------------------------------

st.divider()

with st.container():
    st.subheader("🎤 Voice Input")
    st.caption(
        "Click **Start Recording**, speak your question, "
        "then click **Stop Recording**."
    )

    # mic_recorder returns a dict {"bytes", "sample_rate", "sample_width", "id"}
    # or None if nothing has been recorded yet.
    # just_once=True means Streamlit only acts on a *new* recording,
    # not on every page rerun — this replaces our manual hash deduplication.
    audio_result = mic_recorder(
        start_prompt="▶ Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        format="wav",
        key="voice_recorder",
    )

    if audio_result:
        audio_bytes = audio_result["bytes"]

        st.audio(audio_bytes, format="audio/wav")

        with st.spinner(
            f"Transcribing {st.session_state.language} speech…"
        ):
            try:
                user_text = transcribe_audio(
                    audio_bytes=audio_bytes,
                    mime_type="audio/wav",
                    language_name=LANGUAGES[st.session_state.language][
                        "gemini_lang"
                    ],
                )
            except RuntimeError as exc:
                st.error(f"⚠️ Transcription failed: {exc}")
                user_text = ""

        if not user_text:
            st.warning(
                "Could not understand the audio. "
                "Please speak clearly and try again."
            )
        else:
            st.info(f"📝 Transcribed: *{user_text}*")
            _handle_input(user_text)
            st.rerun()
