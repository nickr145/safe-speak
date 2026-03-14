"""Speech-to-Text module using ElevenLabs API."""

from elevenlabs import ElevenLabs

from app.config import settings

_client: ElevenLabs | None = None


def _get_client() -> ElevenLabs:
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    return _client


def transcribe_audio(audio_bytes: bytes, sample_rate: int = 16000) -> str:
    """Transcribe audio bytes to text using ElevenLabs STT.

    Args:
        audio_bytes: Raw audio file bytes (WAV, MP3, WebM, etc.)
        sample_rate: Unused, kept for API compatibility.

    Returns:
        Transcribed text string.
    """
    import io
    client = _get_client()

    # ElevenLabs SDK expects a file-like tuple: (filename, file_obj, mime_type)
    audio_file = io.BytesIO(audio_bytes)

    result = client.speech_to_text.convert(
        file=("recording.webm", audio_file, "audio/webm"),
        model_id="scribe_v1",
        language_code="eng",
    )

    return result.text.strip()
