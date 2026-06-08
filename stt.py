"""
stt.py — Speech-to-Text via Gemini's Files API + native audio understanding.

WHY Files API instead of inline bytes?
  Sending raw audio inline in the request body causes the server to drop the
  connection for recordings larger than ~1-2 MB ("Server disconnected without
  sending a response"). Uploading via the Files API first is the recommended
  approach for any binary payload and is robust regardless of recording length.

Reliability strategy:
  1. Upload audio to Gemini Files API (always reliable, separate from inference).
  2. Call generate_content with the uploaded file URI.
  3. On first attempt use gemini-2.5-flash-lite (lighter, higher availability).
  4. If Gemini returns a 503 / "high demand" error, automatically retry once
     with gemini-2.5-flash (the heavier fallback model).
  5. Transient network errors are retried up to GEMINI_MAX_RETRIES times with
     exponential backoff before raising to the caller.
"""

import io
import logging
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import GEMINI_MAX_RETRIES, GEMINI_MODEL_FALLBACK, GEMINI_MODEL_PRIMARY

load_dotenv()

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Error substrings that mean "server overloaded — try again or use fallback"
_OVERLOAD_SIGNALS = (
    "high demand",
    "overloaded",
    "503",
    "service unavailable",
    "resource exhausted",
)


def _is_overload_error(exc: Exception) -> bool:
    return any(sig in str(exc).lower() for sig in _OVERLOAD_SIGNALS)


def _is_transient_error(exc: Exception) -> bool:
    transient = (
        "server disconnected",
        "remote protocol",
        "connection reset",
        "timeout",
        "temporarily unavailable",
    )
    return any(sig in str(exc).lower() for sig in transient)


def _upload_audio(audio_bytes: bytes, mime_type: str) -> str:
    """
    Upload audio bytes to the Gemini Files API.

    Returns the file URI string (e.g. "files/abc123") to be passed to
    generate_content.  The file is deleted after use to avoid clutter.
    """
    audio_stream = io.BytesIO(audio_bytes)

    uploaded = _client.files.upload(
        file=audio_stream,
        config=types.UploadFileConfig(mime_type=mime_type),
    )
    return uploaded.uri, uploaded.name


def _delete_file(file_name: str) -> None:
    """Best-effort cleanup of a Files API object."""
    try:
        _client.files.delete(name=file_name)
    except Exception:
        pass  # Not critical if cleanup fails


def _call_gemini(file_uri: str, mime_type: str, prompt: str, model: str) -> str:
    """Single generate_content call using an already-uploaded file URI."""
    response = _client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_uri(file_uri=file_uri, mime_type=mime_type),
            prompt,
        ],
    )
    return response.text.strip()


def transcribe_audio(
    audio_bytes: bytes,
    mime_type: str,
    language_name: str,
) -> str:
    """
    Transcribe audio bytes using Gemini's multimodal capability.

    Parameters
    ----------
    audio_bytes   : raw audio data (WAV / WebM / MP3 etc.)
    mime_type     : MIME type string, e.g. "audio/wav"
    language_name : human-readable language name, e.g. "Yoruba"

    Returns
    -------
    Transcribed text string, or "" if audio was silent/unintelligible.

    Raises
    ------
    RuntimeError if all retries and the fallback model are exhausted.
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

    # --- Step 1: Upload audio (separate from inference, very reliable) ---
    try:
        file_uri, file_name = _upload_audio(audio_bytes, mime_type)
    except Exception as exc:
        logger.error("Files API upload failed: %s", exc, exc_info=True)
        raise RuntimeError(f"Audio upload failed: {exc}") from exc

    # --- Step 2: Transcribe with retry + model fallback ---
    models_to_try = [GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK]
    last_exc: Exception | None = None

    try:
        for model in models_to_try:
            for attempt in range(1, GEMINI_MAX_RETRIES + 1):
                try:
                    text = _call_gemini(file_uri, mime_type, prompt, model)

                    if text.lower() in ("[inaudible]", "inaudible", ""):
                        logger.warning("STT returned inaudible/empty result.")
                        return ""

                    logger.info(
                        "STT success (model=%s, attempt=%d)", model, attempt
                    )
                    return text

                except Exception as exc:
                    last_exc = exc

                    if _is_overload_error(exc):
                        # Capacity spike — try fallback model immediately
                        logger.warning(
                            "STT overload on %s (attempt %d), %s",
                            model,
                            attempt,
                            "switching model" if attempt == GEMINI_MAX_RETRIES
                            else "retrying…",
                        )
                        if attempt == GEMINI_MAX_RETRIES:
                            break   # move to next model in the chain
                        time.sleep(2 ** attempt)  # 2s, 4s backoff

                    elif _is_transient_error(exc):
                        # Network blip — retry same model
                        logger.warning(
                            "STT transient error on %s (attempt %d): %s",
                            model, attempt, exc,
                        )
                        if attempt == GEMINI_MAX_RETRIES:
                            break
                        time.sleep(2 ** attempt)

                    else:
                        # Non-retriable error — fail immediately
                        logger.error("STT non-retriable error: %s", exc, exc_info=True)
                        raise RuntimeError(f"Speech transcription failed: {exc}") from exc

        raise RuntimeError(
            f"STT failed after all retries and fallback models. "
            f"Last error: {last_exc}"
        )

    finally:
        _delete_file(file_name)
