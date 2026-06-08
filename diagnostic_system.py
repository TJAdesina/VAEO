"""
diagnostic_system.py — Multilingual Agricultural Extension Officer AI brain.

Two response paths:
  get_response_stream()    — streaming plain text, used for all user interactions
  get_ai_response_plain()  — blocking plain text, used for language-switch triggers
  process_user_message()   — thin wrapper around get_ai_response_plain()

Language enforcement and the mismatch-advisory rule are injected dynamically
via build_system_prompt() so the BASE_SYSTEM_PROMPT stays untouched.
"""

import logging
import os
import time
from collections.abc import Generator

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import GEMINI_MAX_RETRIES, GEMINI_MODEL_FALLBACK, GEMINI_MODEL_PRIMARY

load_dotenv()
logger = logging.getLogger(__name__)

# Module-level client — initialised once on import (serves as @st.cache_resource
# equivalent; importing this module at Streamlit startup pre-warms the connection).
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------------------------------------------------------------------
# Base system prompt — DO NOT EDIT (per project brief).
# Language enforcement is prepended by build_system_prompt().
# ---------------------------------------------------------------------------

BASE_SYSTEM_PROMPT = """
You are an experienced, patient, and practical Nigerian agricultural extension officer helping rural farmers solve farming problems.

Your goal is NOT simply to answer questions.

Your goal is to:

- understand the farmer's problem
- ask useful diagnostic questions
- identify the likely cause
- provide practical recommendations farmers can follow

IMPORTANT BEHAVIOR RULES:

1. Never immediately give a diagnosis after the farmer's first message.
2. Ask at least one follow-up diagnostic question before diagnosing.
3. Ask only ONE question at a time.
4. Ask at most 3 diagnostic questions before giving your best likely diagnosis.
5. Each question should reduce uncertainty.
6. Avoid repetitive or unnecessary questions.
7. If enough information is available early, diagnose sooner.
8. Sound calm, practical, supportive, and conversational.
9. Avoid sounding robotic or overly technical.
10. Give recommendations farmers can realistically follow.
11. Prefer affordable and locally practical suggestions when possible.

IMPORTANT DIAGNOSTIC STRATEGY:

Prioritize questions in this order when possible:

1. Crop identification
2. Plant growth stage
3. Main symptom
4. Location of symptom
5. Spread pattern
6. Pest signs
7. Watering conditions
8. Fertilizer usage

VOICE + LOW-LITERACY RULES:

Farmers may:
- use voice input with errors
- mix languages
- use local expressions
- give short or unclear answers

Interpret meaning intelligently when possible.

Only ask for clarification if meaning is truly unclear.

Example corrections:
"maze" → "maize"
"army warm" → "armyworm"
"leaf dey yellow" → "leaves are turning yellow"

CLARIFICATION HANDLING:

If the farmer says:
- "I don't understand"
- "I don't know"

Then:
1. Do NOT change the topic
2. Re-explain the same question/answer in simpler words
3. Use practical examples

VOICE OUTPUT RULES:

Responses will be spoken aloud.

Therefore:
- Keep responses short
- Use simple sentences
- Avoid technical language
- Give at most 3 actions
- Put most important action first
- No long explanations unless requested

WHEN GIVING A DIAGNOSIS:

Speak naturally like a real extension officer.

Include:
- likely problem
- reason (short)
- actions (max 3)

Do NOT use headings or labels.
Do NOT use bullet formatting.

Example style:

This looks like nitrogen deficiency because the older leaves are turning yellow first. You should apply nitrogen-rich fertilizer if available. Compost or manure can also help. Then check if the new leaves become greener over the next few days.
"""

# ---------------------------------------------------------------------------
# Dynamic prompt builder
# ---------------------------------------------------------------------------

def build_system_prompt(language: str, include_advisory: bool = True) -> str:
    """
    Prepend a language-enforcement block to BASE_SYSTEM_PROMPT.

    include_advisory=False skips the mismatch-advisory rule (used for
    internal language-switch triggers where the language is already known).
    """
    advisory_rule = ""
    if include_advisory:
        advisory_rule = f"""
MISMATCH ADVISORY RULE:
If the user's input is CLEARLY written in a language other than {language}:
  • Make the VERY FIRST LINE of your response exactly:
    ADVISORY:[2-letter ISO 639-1 code of the user's language]:[short message in the user's language, telling them they appear to be in the wrong language mode and should switch]
  • Then start a new line and give your normal {language} response.
  • If the input is in {language}, or the language is ambiguous, skip the ADVISORY line entirely.
  • Example first line: ADVISORY:en:You seem to be typing in English. Please switch to English mode.
"""

    enforcement = f"""
=== ACTIVE LANGUAGE MODE: {language.upper()} ===
HARD RULE: You MUST respond EXCLUSIVELY in {language}.
This overrides every other instruction in this prompt — no exceptions.
{advisory_rule}
LANGUAGE SWITCH HANDLER:
If the user's message starts with "[LANG_SWITCH]", respond in {language} ONLY:
  1. Warmly acknowledge the language switch in ONE brief sentence.
  2. Re-deliver the content of your previous response, fully translated into {language}.
=== END LANGUAGE MODE ===

"""
    return enforcement + BASE_SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Error classification (shared with stt.py logic)
# ---------------------------------------------------------------------------

_OVERLOAD  = ("high demand", "overloaded", "503", "service unavailable", "resource exhausted")
_TRANSIENT = ("server disconnected", "remote protocol", "connection reset", "timeout",
              "temporarily unavailable")

def _is_overload(e: Exception) -> bool:
    return any(s in str(e).lower() for s in _OVERLOAD)

def _is_transient(e: Exception) -> bool:
    return any(s in str(e).lower() for s in _TRANSIENT)


# ---------------------------------------------------------------------------
# Shared message formatter
# ---------------------------------------------------------------------------

def _build_messages(history: list[dict]) -> list[dict]:
    out = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else msg["role"]
        out.append({"role": role, "parts": [{"text": msg["content"]}]})
    return out


# ---------------------------------------------------------------------------
# Streaming path — primary entry point for user interactions
# ---------------------------------------------------------------------------

def get_response_stream(
    history: list[dict],
    language: str,
) -> Generator[str, None, None]:
    """
    Yield plain-text chunks from Gemini. Falls back to the heavier model on 503.
    Raises RuntimeError only after all retries and both models are exhausted.
    """
    messages = _build_messages(history)
    system_prompt = build_system_prompt(language, include_advisory=True)
    models = [GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK]
    last_exc: Exception | None = None

    for model in models:
        for attempt in range(1, GEMINI_MAX_RETRIES + 1):
            try:
                stream = _client.models.generate_content_stream(
                    model=model,
                    contents=messages,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.4,
                    ),
                )
                for chunk in stream:
                    try:
                        if chunk.text:
                            yield chunk.text
                    except Exception:
                        pass
                return  # stream completed successfully

            except Exception as exc:
                last_exc = exc
                if _is_overload(exc) or _is_transient(exc):
                    logger.warning("Stream error on %s attempt %d: %s", model, attempt, exc)
                    if attempt < GEMINI_MAX_RETRIES:
                        time.sleep(2 ** attempt)
                    else:
                        break   # try next model
                else:
                    raise RuntimeError(f"AI error: {exc}") from exc

    raise RuntimeError(f"AI unavailable after all retries. Last error: {last_exc}")


# ---------------------------------------------------------------------------
# Non-streaming path — used only for language-switch acknowledgment
# ---------------------------------------------------------------------------

def get_ai_response_plain(history: list[dict], language: str) -> str:
    """Blocking call. Returns the full response as a plain-text string."""
    messages = _build_messages(history)
    system_prompt = build_system_prompt(language, include_advisory=False)
    models = [GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK]
    last_exc: Exception | None = None

    for model in models:
        for attempt in range(1, GEMINI_MAX_RETRIES + 1):
            try:
                response = _client.models.generate_content(
                    model=model,
                    contents=messages,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.4,
                    ),
                )
                return response.text.strip()
            except Exception as exc:
                last_exc = exc
                if _is_overload(exc) or _is_transient(exc):
                    if attempt < GEMINI_MAX_RETRIES:
                        time.sleep(2 ** attempt)
                    else:
                        break
                else:
                    break   # non-retriable; try fallback model

    logger.error("Non-streaming AI failed. Last error: %s", last_exc)
    return "I'm having trouble connecting right now. Please try again."


def process_user_message(
    user_text: str,
    conversation_history: list[dict],
    language: str = "English",
) -> tuple[dict, list[dict]]:
    """Wrapper kept for compatibility. Returns (response_dict, updated_history)."""
    history = list(conversation_history)
    history.append({"role": "user", "content": user_text})
    text = get_ai_response_plain(history, language)
    history.append({"role": "assistant", "content": text})
    return {"content": text}, history
