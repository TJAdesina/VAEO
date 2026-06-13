"""
tts.py — Text-to-Speech via Spitch.

Spitch is chosen because it has the best African-language voice quality.
The generate() call returns a binary response object; .read() yields WAV bytes.

Spitch SDK docs: https://docs.spi-tch.com/features/speech
"""

import logging
import os

from dotenv import load_dotenv
from spitch import Spitch

from config import LANGUAGES

load_dotenv()

logger = logging.getLogger(__name__)

# Module-level Spitch client singleton
_client = Spitch(api_key=os.getenv("SPITCH_API_KEY"))


def synthesize_speech(text: str, language_name: str) -> bytes:
    """
    Convert text to speech using Spitch and return raw WAV bytes.

    Parameters
    ----------
    text          : text to synthesize (should already be tone-marked if Yoruba)
    language_name : key into LANGUAGES config, e.g. "Yoruba"

    Returns
    -------
    WAV audio as bytes.

    Raises
    ------
    RuntimeError on any Spitch API failure.
    """
    lang_cfg = LANGUAGES.get(language_name)
    if not lang_cfg:
        raise ValueError(f"Unsupported language: {language_name!r}")

    language_code: str = lang_cfg["code"]
    voice: str = lang_cfg["spitch_voice"]

    try:
        response = _client.speech.generate(
            text=text,
            language=language_code,
            voice=voice,
        )
        audio_bytes: bytes = response.read()
        return audio_bytes

    except Exception as exc:
        logger.error(
            "TTS error (lang=%s, voice=%s): %s", language_code, voice, exc,
            exc_info=True,
        )
        raise RuntimeError(f"Speech synthesis failed: {exc}") from exc
