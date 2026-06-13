"""
tts.py — Text-to-Speech via Spitch.

synthesize_speech_parallel() is the primary entry point.
It splits the response into sentences and synthesises each in parallel,
reducing TTS wait time from sum(sentence_times) → max(sentence_times).

Spitch charges per character regardless of call count, so parallelising
sentences has the same cost as a single call for the full text.

Audio format strategy
─────────────────────
We request format="pcm_s16le" from Spitch: raw signed 16-bit little-endian
PCM at 22 050 Hz mono (Spitch's fixed output spec).  This eliminates all
container-parsing complexity — concatenating sentences is just bytes addition.
After combining, we wrap the raw PCM in a standard WAV header so the browser
and st.audio() can play it directly.
"""

import io
import logging
import os
import re
import struct
import wave
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from spitch import Spitch

from config import LANGUAGES

load_dotenv()
logger = logging.getLogger(__name__)

# Module-level singleton — initialised once on import (pre-warmed on startup).
_client = Spitch(api_key=os.getenv("SPITCH_API_KEY"))

_MIN_CHUNK_CHARS = 15   # merge very short fragments with the next sentence
_MAX_WORKERS     = 3    # parallel Spitch connections cap

# Spitch pcm_s16le output spec (fixed for all voices/languages)
_SAMPLE_RATE  = 22_050
_CHANNELS     = 1
_SAMPLE_WIDTH = 2   # 16-bit = 2 bytes


# ---------------------------------------------------------------------------
# Sentence splitter
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    """
    Split text into synthesis-sized chunks at sentence boundaries.
    Short fragments are merged with the next sentence to avoid tiny TTS calls.
    """
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    merged: list[str] = []
    buf = ""

    for part in raw:
        part = part.strip()
        if not part:
            continue
        buf = (buf + " " + part).strip() if buf else part
        if len(buf) >= _MIN_CHUNK_CHARS:
            merged.append(buf)
            buf = ""

    if buf:
        if merged:
            merged[-1] += " " + buf
        else:
            merged.append(buf)

    return merged or [text.strip()]


# ---------------------------------------------------------------------------
# PCM → WAV wrapper
# ---------------------------------------------------------------------------

def _pcm_to_wav(pcm_bytes: bytes) -> bytes:
    """Wrap raw pcm_s16le bytes in a standard WAV container."""
    out = io.BytesIO()
    with wave.open(out, "wb") as wf:
        wf.setnchannels(_CHANNELS)
        wf.setsampwidth(_SAMPLE_WIDTH)
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(pcm_bytes)
    return out.getvalue()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def synthesize_speech(text: str, language_name: str) -> bytes:
    """
    Synthesise a single text string and return raw PCM bytes (pcm_s16le).
    Callers must not assume a WAV container — use synthesize_speech_parallel()
    which handles wrapping.
    """
    cfg = LANGUAGES.get(language_name)
    if not cfg:
        raise ValueError(f"Unsupported language: {language_name!r}")
    try:
        return _client.speech.generate(
            text=text,
            language=cfg["code"],
            voice=cfg["spitch_voice"],
            format="pcm_s16le",
        ).read()
    except Exception as exc:
        logger.error("Spitch TTS error (%s): %s", language_name, exc, exc_info=True)
        raise RuntimeError(f"Speech synthesis failed: {exc}") from exc


def synthesize_speech_parallel(text: str, language_name: str) -> bytes:
    """
    Split text into sentences, synthesise each in parallel, concatenate the
    raw PCM streams, wrap in a WAV container, and return the final WAV bytes.

    Concatenating pcm_s16le chunks is just bytes addition — no container
    parsing needed, no RIFF header confusion, no sample-rate mismatch risk.

    For a 3-sentence response with ~1.5 s per call:
      Sequential: ~4.5 s   →   Parallel: ~1.5 s
    """
    sentences = _split_sentences(text)

    if len(sentences) == 1:
        pcm = synthesize_speech(text, language_name)
        return _pcm_to_wav(pcm)

    results: list[bytes | None] = [None] * len(sentences)

    with ThreadPoolExecutor(max_workers=min(len(sentences), _MAX_WORKERS)) as pool:
        future_map = {
            pool.submit(synthesize_speech, s, language_name): i
            for i, s in enumerate(sentences)
        }
        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                logger.warning("Parallel TTS chunk %d failed: %s", idx, exc)

    valid_pcm = [r for r in results if r]
    if not valid_pcm:
        raise RuntimeError("All parallel TTS calls returned no data.")

    # Concatenate in sentence order (results list preserves index order)
    combined_pcm = b"".join(r for r in results if r)
    return _pcm_to_wav(combined_pcm)

