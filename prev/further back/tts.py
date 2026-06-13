"""
tts.py — Text-to-Speech via Spitch.

synthesize_speech_parallel() is the primary entry point.
It splits the response into sentences and synthesises each in parallel,
reducing TTS wait time from sum(sentence_times) → max(sentence_times).

Spitch charges per character regardless of call count, so parallelising
sentences has the same cost as a single call for the full text.
"""

import io
import logging
import os
import re
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
# WAV combiner
# ---------------------------------------------------------------------------

def _combine_wav(chunks: list[bytes]) -> bytes:
    """
    Concatenate WAV byte strings into a single WAV file, preserving the
    sample rate / channel / bit-depth from the first chunk.
    """
    if len(chunks) == 1:
        return chunks[0]

    output = io.BytesIO()
    params = None
    all_frames: list[bytes] = []

    for chunk in chunks:
        try:
            with wave.open(io.BytesIO(chunk), "rb") as wf:
                if params is None:
                    params = wf.getparams()
                all_frames.append(wf.readframes(wf.getnframes()))
        except Exception:
            # If a chunk can't be parsed as WAV, append raw bytes as fallback
            all_frames.append(chunk)

    if params:
        with wave.open(output, "wb") as wf_out:
            wf_out.setparams(params)
            for frames in all_frames:
                wf_out.writeframes(frames)
        return output.getvalue()

    # Last resort: raw concatenation
    return b"".join(chunks)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def synthesize_speech(text: str, language_name: str) -> bytes:
    """Synthesise a single text string and return raw WAV bytes."""
    cfg = LANGUAGES.get(language_name)
    if not cfg:
        raise ValueError(f"Unsupported language: {language_name!r}")
    try:
        return _client.speech.generate(
            text=text,
            language=cfg["code"],
            voice=cfg["spitch_voice"],
        ).read()
    except Exception as exc:
        logger.error("Spitch TTS error (%s): %s", language_name, exc, exc_info=True)
        raise RuntimeError(f"Speech synthesis failed: {exc}") from exc


def synthesize_speech_parallel(text: str, language_name: str) -> bytes:
    """
    Split text into sentences, synthesise each in parallel, return combined WAV.

    For a 3-sentence response with ~1.5 s per call:
      Sequential: ~4.5 s   →   Parallel: ~1.5 s
    """
    sentences = _split_sentences(text)

    if len(sentences) == 1:
        return synthesize_speech(text, language_name)

    results: list[bytes | None] = [None] * len(sentences)

    with ThreadPoolExecutor(max_workers=min(len(sentences), _MAX_WORKERS)) as pool:
        future_map = {
            pool.submit(synthesize_speech, s, language_name): i
            for i, s in enumerate(sentences)
        }
        for future in as_completed(future_map):
            idx = future_map[future]
            results[idx] = future.result()   # raises on TTS error

    valid = [r for r in results if r is not None]
    if not valid:
        raise RuntimeError("All parallel TTS calls returned no data.")

    return _combine_wav(valid)
