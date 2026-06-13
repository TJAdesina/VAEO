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

def _read_wav_frames(data: bytes) -> tuple:
    """
    Safely extract PCM frames from a WAV byte string.

    Python's wave module raises 'argument out of range' when the nframes
    header field doesn't match the actual data size (a known Spitch quirk).
    We work around this by:
      1. Opening the file to read the audio parameters (nchannels, sampwidth,
         framerate) — these header fields are always correct.
      2. Seeking past the 44-byte standard WAV header and reading ALL remaining
         bytes as raw PCM, ignoring the declared nframes entirely.

    Returns (params, raw_pcm_bytes), or (None, b"") on failure.
    """
    try:
        buf = io.BytesIO(data)
        with wave.open(buf, "rb") as wf:
            params = wf.getparams()
        # Seek past the standard 44-byte WAV header and read everything
        buf.seek(44)
        raw_pcm = buf.read()
        return params, raw_pcm
    except Exception as exc:
        logger.warning("WAV parse failed, skipping chunk: %s", exc)
        return None, b""


def _combine_wav(chunks: list) -> bytes:
    """
    Concatenate WAV byte strings into a single WAV file, preserving the
    sample rate / channel / bit-depth from the first valid chunk.
    """
    if len(chunks) == 1:
        return chunks[0]

    base_params = None
    all_pcm = []

    for chunk in chunks:
        if not chunk:
            continue
        params, pcm = _read_wav_frames(chunk)
        if params is not None and pcm:
            if base_params is None:
                base_params = params
            all_pcm.append(pcm)

    if not all_pcm:
        # Nothing parsed — return first non-empty chunk as-is
        return next((c for c in chunks if c), b"")

    if base_params is None or len(all_pcm) == 1:
        return next((c for c in chunks if c), b"")

    combined_pcm = b"".join(all_pcm)
    output = io.BytesIO()
    with wave.open(output, "wb") as wf_out:
        wf_out.setnchannels(base_params.nchannels)
        wf_out.setsampwidth(base_params.sampwidth)
        wf_out.setframerate(base_params.framerate)
        wf_out.writeframes(combined_pcm)
    return output.getvalue()


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

    results = [None] * len(sentences)

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

    valid = [r for r in results if r is not None]
    if not valid:
        raise RuntimeError("All parallel TTS calls returned no data.")

    return _combine_wav(valid)
