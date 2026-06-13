"""
main.py — FastAPI wrapper for VAEO.

Drop this file next to your existing config.py, diagnostic_system.py, stt.py, tts.py.
It imports them directly and exposes a small HTTP surface for the React frontend.

Run locally:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, HTTPException, Query, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import LANGUAGES, WELCOME_MESSAGES, UI_STRINGS
import diagnostic_system
import stt as stt_mod
import tts as tts_mod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vaeo")

app = FastAPI(title="VAEO", version="1.0.0")

# CORS — only needed in dev (Vite on :5173 hitting FastAPI on :8000).
# In production the same FastAPI process serves the SPA, so this is a no-op.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    history: list[Message]
    language: str = "English"


class TTSRequest(BaseModel):
    text: str
    language: str = "English"


# ---------------------------------------------------------------------------
# Static config endpoints
# ---------------------------------------------------------------------------

@app.get("/api/languages")
def languages() -> list[dict[str, Any]]:
    return [
        {"name": name, "code": cfg["code"], "flag": cfg.get("flag", "")}
        for name, cfg in LANGUAGES.items()
    ]


@app.get("/api/welcome")
def welcome(language: str = Query("English")) -> dict[str, str]:
    text = WELCOME_MESSAGES.get(language) or WELCOME_MESSAGES["English"]
    return {"text": text}


@app.get("/api/ui-strings")
def ui_strings(language: str = Query("English")) -> dict[str, str]:
    return UI_STRINGS.get(language) or UI_STRINGS["English"]


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

def _history_to_dicts(history: list[Message]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in history]


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict[str, str]:
    try:
        text = diagnostic_system.get_ai_response_plain(
            _history_to_dicts(req.history), req.language
        )
        return {"text": text}
    except Exception as exc:
        logger.exception("chat failed")
        raise HTTPException(500, str(exc))


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    hist = _history_to_dicts(req.history)
    language = req.language

    def event_gen():
        try:
            for chunk in diagnostic_system.get_response_stream(hist, language):
                if not chunk:
                    continue
                # SSE escape: each newline in a chunk needs its own `data:` line
                for line in chunk.split("\n"):
                    yield f"data: {line}\n"
                yield "\n"
            yield "event: done\ndata: end\n\n"
        except Exception as exc:
            logger.exception("stream failed")
            yield f"event: error\ndata: {exc}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------------------------------------------------------------------------
# Speech-to-Text
# ---------------------------------------------------------------------------

@app.post("/api/transcribe")
async def transcribe_endpoint(
    audio: UploadFile = File(...),
    language: str = Form("English"),
    mime_type: str = Form(""),
) -> dict[str, str]:
    try:
        data = await audio.read()
        mime = mime_type or audio.content_type or "audio/webm"
        text = stt_mod.transcribe_audio(data, mime, language)
        return {"text": text}
    except Exception as exc:
        logger.exception("transcribe failed")
        raise HTTPException(500, str(exc))


# ---------------------------------------------------------------------------
# Text-to-Speech
# ---------------------------------------------------------------------------

@app.post("/api/tts")
def tts_endpoint(req: TTSRequest):
    try:
        wav = tts_mod.synthesize_speech_parallel(req.text, req.language)
        return Response(content=wav, media_type="audio/wav")
    except Exception as exc:
        logger.exception("tts failed")
        raise HTTPException(500, str(exc))


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"ok": True}


# ---------------------------------------------------------------------------
# Static SPA — must be LAST so /api/* routes win
# ---------------------------------------------------------------------------

STATIC_DIR = Path(__file__).parent / "static"

if STATIC_DIR.is_dir():
    # Serve the Vite assets folder
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str, request: Request):
        if full_path.startswith("api/"):
            raise HTTPException(404)
        candidate = STATIC_DIR / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        index = STATIC_DIR / "index.html"
        if index.is_file():
            return FileResponse(index)
        return JSONResponse({"error": "frontend not built"}, status_code=404)
else:
    @app.get("/")
    def root_missing():
        return JSONResponse(
            {
                "error": "Frontend not built. Run `cd frontend && npm install && npm run build` "
                "to populate ./static/, then restart this server."
            },
            status_code=503,
        )
