"""
diagnostic_system.py — Multilingual Agricultural Extension Officer AI brain.

Wraps the Gemini API to produce structured diagnostic responses.
Called by app.py; has no dependency on Streamlit.
"""

import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import GEMINI_MODEL

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gemini client (module-level singleton)
# ---------------------------------------------------------------------------

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------------------------------------------------------------------
# System prompt — DO NOT EDIT unless absolutely necessary (per brief)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
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

LANGUAGE RULES (CRITICAL):

You MUST reply ONLY in the language used in the user's MOST RECENT message.

STRICT RULES:

- If the user's latest message is entirely English, respond ONLY in English.
- If the user's latest message is entirely Yoruba, respond ONLY in Yoruba.
- If the user's latest message is entirely Hausa, respond ONLY in Hausa.
- If the user's latest message is entirely Igbo, respond ONLY in Igbo.

NEVER mix languages unless the user mixed them first.

NEVER add translations.

NEVER repeat the same sentence in another language.

Examples:

User: "My maize leaves are yellow"
Correct response:
"What crop is affected?"

Wrong response:
"Iru crop wo ni? What crop is affected?"

If the user mixes languages, respond in the dominant language used by the user.

If the language of the user's message is unclear:
- infer from key words and structure
- if still uncertain, respond in the language used in the majority of the message

When responding in Yoruba, Hausa, or Igbo:
- Use simple everyday conversational form
- Avoid formal academic translation style
- Prefer natural spoken expressions used by rural farmers

This rule overrides ALL other instructions.

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
# Structured output schema
# ---------------------------------------------------------------------------

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "type": {
            "type": "STRING",
            "enum": ["question", "diagnosis"],
        },
        "content": {
            "type": "STRING",
        },
        "question_count": {
            "type": "INTEGER",
        },
    },
    "required": ["type", "content", "question_count"],
}


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def _build_gemini_messages(conversation_history: list[dict]) -> list[dict]:
    """Convert Streamlit-style history (role/content) to Gemini format."""
    messages = []
    for msg in conversation_history:
        role = msg["role"].lower()
        if role == "assistant":
            role = "model"
        messages.append({"role": role, "parts": [{"text": msg["content"]}]})
    return messages


def get_ai_response(conversation_history: list[dict]) -> dict:
    """
    Call Gemini with the full conversation and return a parsed response dict.

    Returns a dict with keys: type, content, question_count.
    Falls back gracefully on any API error.
    """
    messages = _build_gemini_messages(conversation_history)
    try:
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                temperature=0.4,
            ),
        )
        return response.parsed

    except Exception as exc:
        logger.error("Gemini AI error: %s", exc, exc_info=True)
        return {
            "type": "diagnosis",
            "content": (
                "I'm having trouble connecting right now. "
                "Please check your internet connection and try again."
            ),
            "question_count": 0,
        }


def process_user_message(
    user_text: str,
    conversation_history: list[dict],
) -> tuple[dict, list[dict]]:
    """
    Append the user's message, get an AI reply, append that too.

    Returns (ai_response_dict, updated_history).
    Does NOT mutate the original list — works on a copy.
    """
    history = list(conversation_history)
    history.append({"role": "user", "content": user_text})

    ai_response = get_ai_response(history)
    assistant_text = ai_response.get("content", "")

    history.append({"role": "assistant", "content": assistant_text})
    return ai_response, history
