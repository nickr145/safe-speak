"""FastAPI backend for AI Phone Call Practice."""

import logging
import json

from fastapi import FastAPI, UploadFile, File, HTTPException

logger = logging.getLogger(__name__)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import settings
from app.schemas import (
    StartCallRequest,
    StartCallResponse,
    UserTurnResponse,
    HintRequest,
    HintResponse,
    EndCallRequest,
    EndCallResponse,
    ScenarioInfo,
    TranscribeResponse,
    TTSRequest,
)
from app.scenarios import list_scenarios
from app.stt import transcribe_audio
from app.tts import synthesize_speech
from app.call_manager import (
    create_session,
    get_session,
    start_call,
    process_user_turn,
    get_hint,
    end_call,
)

app = FastAPI(
    title="AI Phone Call Practice API",
    description="Backend API for simulated voice call practice for newcomers",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Scenarios ──────────────────────────────────────────────────────────────────


@app.get("/api/scenarios", response_model=list[ScenarioInfo])
def get_scenarios():
    """List all available call scenarios."""
    return list_scenarios()


# ── Call Lifecycle ─────────────────────────────────────────────────────────────


@app.post("/api/call/start", response_model=StartCallResponse)
def api_start_call(req: StartCallRequest):
    """Start a new call session for a given scenario (JSON body)."""
    print(json.dumps(req.model_dump()))
    return _start_call_common(req.scenario_id, req.target_language)


@app.post("/api/call/start/simple", response_model=StartCallResponse)
def api_start_call_simple(scenario_id: str, target_language: str | None = None):
    """Start a new call session using a simple POST with query param.

    This avoids CORS preflight complexity for quick browser tests.
    """
    return _start_call_common(scenario_id, target_language)


def _start_call_common(
    scenario_id: str,
    target_language: str | None = None,
) -> StartCallResponse:
    try:
        session = create_session(scenario_id, target_language=target_language)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    greeting_text = start_call(session)

    return StartCallResponse(
        session_id=session.session_id,
        scenario_id=session.scenario.id,
        scenario_title=session.scenario.title,
        greeting_text=greeting_text,
        state=session.state.value,
        target_language=session.target_language,
    )


@app.post("/api/call/turn", response_model=UserTurnResponse)
async def api_user_turn(session_id: str, audio: UploadFile = File(...)):
    """Process a user's voice turn: transcribe audio -> get AI response.

    Send audio as a multipart file upload with the session_id as a query param.
    """
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Transcribe user audio
    audio_bytes = await audio.read()
    user_text = transcribe_audio(audio_bytes)

    if not user_text:
        logger.warning(
            "Empty transcript from STT (audio_bytes=%s)",
            len(audio_bytes),
        )
        user_text = "I didn't catch that."

    # Process the turn through the call manager
    result = process_user_turn(session, user_text)

    print(result)
    print(user_text)
    print(result["ai_text"])
    print(result["ai_text_translated"])
    print(result["state"])
    print(result["goal_achieved"])
    print(result["hint"])

    return UserTurnResponse(
        session_id=session.session_id,
        user_text=user_text,
        ai_text=result["ai_text"],
        ai_text_translated=result["ai_text_translated"],
        state=result["state"],
        goal_achieved=result["goal_achieved"],
        hint=result["hint"],
    )


@app.post("/api/call/turn/text", response_model=UserTurnResponse)
def api_user_turn_text(session_id: str, text: str):
    """Process a user's text turn directly (for testing or text-based fallback).

    Send text as a query param alongside session_id.
    """
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    result = process_user_turn(session, text)

    return UserTurnResponse(
        session_id=session.session_id,
        user_text=text,
        ai_text=result["ai_text"],
        ai_text_translated=result["ai_text_translated"],
        state=result["state"],
        goal_achieved=result["goal_achieved"],
        hint=result["hint"],
    )


@app.post("/api/call/hint", response_model=HintResponse)
def api_get_hint(req: HintRequest):
    """Get a spoken hint for the user when they're stuck."""
    session = get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    hint_text = get_hint(session)
    return HintResponse(hint_text=hint_text)


@app.post("/api/call/end", response_model=EndCallResponse)
def api_end_call(req: EndCallRequest):
    """End the call and get the debrief."""
    session = get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    result = end_call(session)

    return EndCallResponse(
        session_id=req.session_id,
        state=result["state"],
        debrief=result["debrief"],
        transcript=result["transcript"],
    )


# ── Standalone STT / TTS ──────────────────────────────────────────────────────


@app.post("/api/stt/transcribe", response_model=TranscribeResponse)
async def api_transcribe(audio: UploadFile = File(...)):
    """Transcribe an audio file to text (standalone STT endpoint)."""
    audio_bytes = await audio.read()
    text = transcribe_audio(audio_bytes)
    return TranscribeResponse(text=text)


@app.post("/api/tts/synthesize")
def api_synthesize(req: TTSRequest):
    """Synthesize text to speech audio (returns MP3 bytes)."""
    audio_bytes = synthesize_speech(req.text, req.voice_id)
    return Response(content=audio_bytes, media_type="audio/mpeg")


# ── Health ─────────────────────────────────────────────────────────────────────


@app.get("/api/health")
def health():
    return {"status": "ok"}
