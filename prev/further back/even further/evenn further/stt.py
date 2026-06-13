"""
stt.py — Speech-to-Text via Gemini's native audio understanding.

Matches the working approach from gemini_stt_test.py:
  - Sends raw audio bytes + a language-aware prompt to Gemini 2.5 Flash
  - Returns only the clean transcription string (no English translation)
  - Works for Yoruba, Hausa, Igbo, and English
"""

import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import GEMINI_MODEL

load_dotenv()

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def transcribe_audio(
    audio_bytes: bytes,
    mime_type: str,
    language_name: str,
) -> str:
    """
    Transcribe audio bytes using Gemini's multimodal capability.

    Parameters
    ----------
    audio_bytes   : raw audio data (WAV/MP3/etc.)
    mime_type     : MIME type string, e.g. "audio/wav"
    language_name : human-readable language name, e.g. "Yoruba"

    Returns
    -------
    Transcribed text string. Returns empty string on failure.
    """
    prompt = f"""
You are an expert native {language_name} speech recognition engine.

Listen to the audio carefully and transcribe ONLY the spoken words into clean {language_name} text.

STRICT RULES:
- Output ONLY the transcription. Nothing else.
- Do NOT translate into English.
- Do NOT add explanations, labels, or headers.
- If the speaker mixes languages, transcribe exactly as spoken.
- Fix obvious acoustic slurs and apply correct diacritics for {language_name} where applicable.
- If the audio is silent or unintelligible, output exactly: [inaudible]
"""

    try:
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                prompt,
            ],
        )
        text = response.text.strip()

        # Treat Gemini's "[inaudible]" marker as empty so callers can handle it
        if text.lower() in ("[inaudible]", "inaudible", ""):
            logger.warning("STT returned inaudible or empty result.")
            return ""

        return text

    except Exception as exc:
        logger.error("STT error: %s", exc, exc_info=True)
        raise RuntimeError(f"Speech transcription failed: {exc}") from exc
