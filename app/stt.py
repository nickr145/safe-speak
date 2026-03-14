"""Speech-to-Text module using ElevenLabs STT (Scribe v2) via Python SDK."""

from io import BytesIO
from typing import Any

from elevenlabs.client import ElevenLabs

from app.config import settings

_client: ElevenLabs | None = None


def _get_client() -> ElevenLabs:
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    return _client


def transcribe_audio(audio_bytes: bytes, sample_rate: int = 16000) -> str:  # sample_rate kept for compatibility
    """Transcribe audio bytes to text using ElevenLabs Scribe v2.

    Args:
        audio_bytes: Raw audio file bytes (WAV, MP3, etc.).
        sample_rate: Unused; kept for call-site compatibility.

    Returns:
        Transcribed text string.
    """
    client = _get_client()

    audio_file = BytesIO(audio_bytes)

    result: Any = client.speech_to_text.convert(
        file=audio_file,
        model_id="scribe_v2",
        language_code="eng",
        tag_audio_events=True,
        diarize=False,
    )

    # Preferred path: SDK model with .text attribute
    text_attr = getattr(result, "text", None)
    if isinstance(text_attr, str):
        return text_attr.strip()

    # The SDK typically returns a dict-like object; try common shapes.
    if isinstance(result, str):
        return result.strip()

    if isinstance(result, dict):
        if "text" in result and isinstance(result["text"], str):
            return result["text"].strip()
        if "transcript" in result and isinstance(result["transcript"], str):
            return result["transcript"].strip()

    # Fallback: best-effort stringification
    return str(result).strip()
