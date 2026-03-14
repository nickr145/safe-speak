from pydantic import BaseModel


class StartCallRequest(BaseModel):
    scenario_id: str
    # Optional target language for bilingual replies, e.g. "Spanish", "French"
    target_language: str | None = None


class StartCallResponse(BaseModel):
    session_id: str
    scenario_id: str
    scenario_title: str
    greeting_text: str
    state: str
    target_language: str | None = None


class UserTurnRequest(BaseModel):
    session_id: str


class UserTurnResponse(BaseModel):
    session_id: str
    user_text: str
    # AI reply in English (primary language)
    ai_text: str
    # Same reply translated into the user's target language, if requested
    ai_text_translated: str | None = None
    state: str
    goal_achieved: bool
    hint: str | None = None


class HintRequest(BaseModel):
    session_id: str


class HintResponse(BaseModel):
    hint_text: str


class EndCallRequest(BaseModel):
    session_id: str


class EndCallResponse(BaseModel):
    session_id: str
    state: str
    debrief: str
    transcript: list[dict]


class ScenarioInfo(BaseModel):
    id: str
    title: str
    role: str
    organization: str


class TranscribeResponse(BaseModel):
    text: str


class TTSRequest(BaseModel):
    text: str
    voice_id: str = "EXAVITQu4vr4xnSDxMaL"


class ErrorResponse(BaseModel):
    detail: str
