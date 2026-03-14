"""Text-to-Speech module using ElevenLabs API."""

from elevenlabs import ElevenLabs

from app.config import settings

_client: ElevenLabs | None = None


def _get_client() -> ElevenLabs:
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    return _client


def synthesize_speech(text: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL") -> bytes:
    """Convert text to speech audio bytes using ElevenLabs.

    Args:
        text: The text to convert to speech.
        voice_id: ElevenLabs voice ID to use.

    Returns:
        MP3 audio bytes.
    """
    client = _get_client()

    audio_iterator = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    # Collect all chunks into bytes
    audio_chunks = []
    for chunk in audio_iterator:
        audio_chunks.append(chunk)

    return b"".join(audio_chunks)
