"""
app.py — VAEO: Virtual Agricultural Extension Officer

Run:  streamlit run app.py

Architecture
────────────
  config.py            Language registry, model names, welcome strings
  diagnostic_system.py Gemini AI brain  (streaming + non-streaming)
  stt.py               Gemini STT       (audio → text via Files API)
  tts.py               Spitch TTS       (text → WAV, parallel sentences)
  app.py               Streamlit UI, state, orchestration  ← this file
"""

import base64
import logging

import streamlit as st
from streamlit_mic_recorder import mic_recorder

from config import (
    ISO_TO_LANGUAGE,
    LANGUAGES,
    WELCOME_MESSAGES,
    HISTORY_LIMIT,
)
from diagnostic_system import get_response_stream, get_ai_response_plain
from stt import transcribe_audio
from tts import synthesize_speech_parallel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Page config (must be first Streamlit call) ───────────────────────────────

st.set_page_config(
    page_title="🌱 VAEO — Agricultural Voice Assistant",
    page_icon="🌱",
    layout="centered",
)

# ─── Session state initialisation ─────────────────────────────────────────────

def _init_state() -> None:
    defaults: dict = {
        "history":       [],      # list[dict]  role | content | audio_b64 | hidden
        "language":      "English",
        "prev_language": None,    # None = first render, prevents spurious switch detection
        "tts_queue":     None,    # WAV bytes to autoplay on the next render cycle
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ─── Cached welcome-message TTS (one call per language per session) ───────────

@st.cache_data(show_spinner=False)
def _get_welcome_audio(language: str) -> bytes | None:
    """
    Generate and cache TTS for the welcome message.
    @st.cache_data ensures this runs only once per language per server lifetime,
    making the welcome instant on every subsequent load.
    """
    try:
        return synthesize_speech_parallel(WELCOME_MESSAGES[language], language)
    except Exception as exc:
        logger.warning("Welcome TTS failed (%s): %s", language, exc)
        return None


# ─── History helpers ──────────────────────────────────────────────────────────

def _get_ai_history() -> list[dict]:
    """
    Build the history slice sent to Gemini:
    - Skips the leading welcome message (not useful AI context).
    - Keeps hidden language-switch triggers (essential AI context).
    - Truncates to the most recent HISTORY_LIMIT turns (15 × 2 = 30 messages).
    """
    h = st.session_state.history

    # Skip welcome message (first entry if it's an assistant message)
    start = 1 if (h and h[0]["role"] == "assistant" and not h[0].get("hidden")) else 0
    sliced = h[start:]

    max_msgs = HISTORY_LIMIT * 2
    if len(sliced) > max_msgs:
        sliced = sliced[-max_msgs:]

    return [{"role": m["role"], "content": m["content"]} for m in sliced]


# ─── Audio helpers ────────────────────────────────────────────────────────────

def _autoplay_audio(wav_bytes: bytes) -> None:
    """Inject a hidden <audio autoplay> element so TTS plays without user action."""
    b64 = base64.b64encode(wav_bytes).decode()
    st.markdown(
        f'<audio autoplay style="display:none">'
        f'<source src="data:audio/wav;base64,{b64}" type="audio/wav">'
        f"</audio>",
        unsafe_allow_html=True,
    )


def _render_replay_widget(b64: str) -> None:
    """
    Compact audio player shown below each assistant message once TTS is ready.
    Uses st.audio() for reliability; appears only when audio_b64 is present.
    """
    st.audio(base64.b64decode(b64), format="audio/wav")


# ─── Advisory helper ──────────────────────────────────────────────────────────

def _show_advisory(advisory: dict) -> None:
    """
    Render the language-mismatch advisory box with a one-click mode-switch button.
    advisory = {"lang": "en", "message": "You seem to be typing in English..."}
    """
    target_lang = ISO_TO_LANGUAGE.get(advisory["lang"])
    st.info(f"🌍  {advisory['message']}")
    if target_lang and target_lang != st.session_state.language:
        if st.button(
            f"🔄 Switch to {target_lang} mode",
            key=f"adv_btn_{len(st.session_state.history)}",
        ):
            st.session_state.language = target_lang
            st.rerun()


# ─── Welcome message management ───────────────────────────────────────────────

def _ensure_welcome() -> None:
    """Add the welcome message to history if it is empty."""
    if st.session_state.history:
        return
    lang = st.session_state.language
    wav  = _get_welcome_audio(lang)
    st.session_state.history.append({
        "role":      "assistant",
        "content":   WELCOME_MESSAGES[lang],
        "audio_b64": base64.b64encode(wav).decode() if wav else None,
    })


def _replace_welcome(new_lang: str) -> None:
    """
    Swap the welcome message for a new language.
    Called when the user changes language before sending any real message.
    """
    wav = _get_welcome_audio(new_lang)
    st.session_state.history[0] = {
        "role":      "assistant",
        "content":   WELCOME_MESSAGES[new_lang],
        "audio_b64": base64.b64encode(wav).decode() if wav else None,
    }


# ─── Language switch handler ──────────────────────────────────────────────────

def _handle_language_switch() -> None:
    """
    Runs at the top of every render cycle.

    Detects a language change by comparing language vs prev_language, then:
    - Before any user messages: silently replaces the welcome message.
    - During a conversation:    calls the AI to acknowledge the switch and
                                re-deliver the last response in the new language.
    """
    current = st.session_state.language

    # First ever render — just record the language and return
    if st.session_state.prev_language is None:
        st.session_state.prev_language = current
        return

    prev = st.session_state.prev_language
    if current == prev:
        return

    # Update tracker immediately so this block doesn't re-trigger on the next rerun
    st.session_state.prev_language = current

    has_user_msgs = any(m["role"] == "user" for m in st.session_state.history)

    if not has_user_msgs:
        # No real conversation yet — just swap the welcome message
        _replace_welcome(current)
        return

    # ── Mid-conversation switch: trigger AI acknowledgment ──────────────────
    last_assistant = next(
        (m["content"] for m in reversed(st.session_state.history)
         if m["role"] == "assistant" and not m.get("hidden")),
        None,
    )

    trigger = (
        f"[LANG_SWITCH] User switched from {prev} to {current}. "
        + (f"Re-deliver your previous response: {last_assistant[:400]}" if last_assistant else "")
    )

    # Add as a hidden user turn (context for AI; not shown in chat UI)
    st.session_state.history.append({
        "role":    "user",
        "content": trigger,
        "hidden":  True,
    })

    ai_history = _get_ai_history()  # includes the trigger above

    with st.spinner(f"Switching to {current}…"):
        response_text = get_ai_response_plain(ai_history, current)
        try:
            wav = synthesize_speech_parallel(response_text, current)
            b64 = base64.b64encode(wav).decode()
            st.session_state.tts_queue = wav   # autoplay on this render cycle
        except Exception as exc:
            logger.warning("TTS failed for language switch: %s", exc)
            b64 = None

    st.session_state.history.append({
        "role":      "assistant",
        "content":   response_text,
        "audio_b64": b64,
    })


# ─── History renderer ─────────────────────────────────────────────────────────

def _render_history() -> None:
    """
    Render the full conversation.
    Hidden messages (language-switch triggers) are skipped.
    Replay widget appears under each assistant message once audio is ready.
    """
    for msg in st.session_state.history:
        if msg.get("hidden"):
            continue
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and msg.get("audio_b64"):
                _render_replay_widget(msg["audio_b64"])


# ─── Streaming response display ───────────────────────────────────────────────

def _stream_response(stream) -> tuple[str, dict | None]:
    """
    Consume a generate_content_stream, render text progressively, and parse
    an optional ADVISORY: prefix on the first line.

    Returns
    -------
    clean_text : assistant response without the ADVISORY line
    advisory   : {"lang": "en", "message": "..."} or None
    """
    placeholder   = st.empty()
    full_text     = ""
    advisory: dict | None = None
    first_line_done = False

    for chunk in stream:
        # get_response_stream already yields plain strings
        if isinstance(chunk, str):
            piece = chunk
        else:
            try:
                piece = chunk.text or ""
            except Exception:
                piece = ""
        if not piece:
            continue

        full_text += piece

        if not first_line_done:
            if "\n" in full_text:
                first_line, rest = full_text.split("\n", 1)
                first_line_done = True
                if first_line.startswith("ADVISORY:"):
                    parts = first_line.split(":", 2)
                    if len(parts) == 3:
                        advisory = {
                            "lang":    parts[1].strip(),
                            "message": parts[2].strip(),
                        }
                    display = rest
                else:
                    display = full_text
                if display.strip():
                    placeholder.write(display + " ▌")
            elif len(full_text) > 100:
                # First line is long with no advisory marker — stop buffering
                first_line_done = True
                placeholder.write(full_text + " ▌")
            # else: still buffering the first line, show nothing yet
        else:
            display = (
                full_text.split("\n", 1)[1]
                if (advisory and "\n" in full_text)
                else full_text
            )
            if display.strip():
                placeholder.write(display + " ▌")

    # Final render (no cursor)
    clean = (
        full_text.split("\n", 1)[1].strip()
        if (advisory and "\n" in full_text)
        else full_text.strip()
    )
    placeholder.write(clean)
    return clean, advisory


# ─── Core input pipeline ──────────────────────────────────────────────────────

def _handle_input(user_text: str) -> None:
    """
    Full pipeline for any user input (typed or transcribed voice).

    Steps
    ─────
    1.  Add + display user message
    2.  Reserve an advisory slot (rendered between user and assistant messages)
    3.  Stream AI response into a live placeholder
    4.  Synthesise TTS in parallel sentences
    5.  Autoplay audio / queue for post-rerun autoplay
    6.  Render compact replay widget
    7.  Fill advisory slot if a language mismatch was detected
    8.  Persist assistant message to session history
    """
    user_text = user_text.strip()
    if not user_text:
        return

    language = st.session_state.language

    # 1 ── User message ────────────────────────────────────────────────────────
    st.session_state.history.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    # 2 ── Advisory slot (positioned between user msg and assistant msg) ───────
    #      st.container() reserves a layout position; we fill it after streaming
    advisory_slot = st.container()

    # 3 ── Stream AI response ──────────────────────────────────────────────────
    ai_history = _get_ai_history()
    b64: str | None  = None
    advisory: dict | None = None

    with st.chat_message("assistant"):
        try:
            stream     = get_response_stream(ai_history, language)
            clean_text, advisory = _stream_response(stream)
        except Exception as exc:
            st.error(f"⚠️ Response error: {exc}")
            logger.error("Stream error: %s", exc, exc_info=True)
            return

        # 4 ── Parallel sentence TTS ───────────────────────────────────────────
        with st.spinner("🔊 Generating voice…"):
            try:
                wav_bytes = synthesize_speech_parallel(clean_text, language)
                b64       = base64.b64encode(wav_bytes).decode()
            except Exception as exc:
                st.warning(f"⚠️ Voice unavailable: {exc}")
                wav_bytes = None

        # 5 ── Autoplay ────────────────────────────────────────────────────────
        if wav_bytes:
            # Always autoplay immediately; tts_queue is reserved for language-switch reruns
            _autoplay_audio(wav_bytes)

        # 6 ── Replay widget (appears only after TTS is available) ─────────────
        if b64:
            _render_replay_widget(b64)

    # 7 ── Fill advisory slot if mismatch was found ────────────────────────────
    if advisory:
        with advisory_slot:
            _show_advisory(advisory)

    # 8 ── Persist to history ──────────────────────────────────────────────────
    st.session_state.history.append({
        "role":      "assistant",
        "content":   clean_text,
        "audio_b64": b64,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Main render cycle
# ─────────────────────────────────────────────────────────────────────────────

# Language switch detection runs first — may add messages to history
_handle_language_switch()

# Welcome message guard — adds greeting if history is empty
_ensure_welcome()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Settings")

    lang_names = list(LANGUAGES.keys())
    chosen = st.selectbox(
        "🌍 Language",
        options=lang_names,
        index=lang_names.index(st.session_state.language),
        format_func=lambda n: f"{LANGUAGES[n]['flag']} {n}",
        help="Changes STT transcription, TTS voice, and AI response language.",
    )
    if chosen != st.session_state.language:
        st.session_state.language = chosen
        st.rerun()

    st.divider()

    if st.button("🗑️ New conversation", use_container_width=True):
        st.session_state.history   = []
        st.session_state.tts_queue = None
        st.rerun()

    st.divider()
    st.caption(
        f"**Mode:** {LANGUAGES[st.session_state.language]['flag']} "
        f"{st.session_state.language}  \n"
        "VAEO · Gemini 2.5 Flash-Lite · Spitch"
    )

# ── Page title ────────────────────────────────────────────────────────────────

st.title("🌱 Agricultural Voice Assistant")
st.caption(
    f"{LANGUAGES[st.session_state.language]['flag']} **{st.session_state.language}** mode  •  "
    "Type or speak your farming question."
)

# ── Conversation display ──────────────────────────────────────────────────────

_render_history()

# ── Autoplay any queued TTS (voice-input rerun or language-switch) ────────────

if st.session_state.tts_queue:
    _autoplay_audio(st.session_state.tts_queue)
    st.session_state.tts_queue = None

# ── Mic button (sits between history and text input) ─────────────────────────
# Placed here so it renders visually below the chat history and above the
# chat_input footer, exactly where we want it.
#
# The white-rectangle bug was caused by mic_recorder returning the same audio
# result on every rerun (including reruns triggered by new messages), which
# made Streamlit re-process the recording and re-render the widget mid-cycle.
# Fix: track the last processed audio ID in session state and ignore duplicates.

audio_result = mic_recorder(
    start_prompt="🎤",
    stop_prompt="⏹",
    just_once=True,
    format="wav",
    key="voice_recorder",
)

# ── Text input (renders in Streamlit's fixed footer) ─────────────────────────

text_input = st.chat_input("Type or speak your farming question…")
if text_input:
    _handle_input(text_input)

# ── Handle voice input ────────────────────────────────────────────────────────
# Guard against reprocessing: mic_recorder with just_once=True still returns
# the same result dict on every rerun until the user records again. We use the
# audio ID (incrementing int provided by the component) to process each
# recording exactly once.

if audio_result:
    audio_id = audio_result.get("id")
    if audio_id != st.session_state.get("_last_audio_id"):
        st.session_state["_last_audio_id"] = audio_id
        audio_bytes = audio_result["bytes"]

        with st.spinner(f"Transcribing {st.session_state.language} speech…"):
            try:
                user_text = transcribe_audio(
                    audio_bytes=audio_bytes,
                    mime_type="audio/wav",
                    language_name=LANGUAGES[st.session_state.language]["gemini_lang"],
                )
            except RuntimeError as exc:
                st.error(f"⚠️ Transcription failed: {exc}")
                user_text = ""

        if not user_text:
            st.warning("Could not understand the audio. Please speak clearly and try again.")
        else:
            st.info(f"📝 Transcribed: *{user_text}*")
            _handle_input(user_text)
