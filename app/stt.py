"""Speech-to-Text module using OpenAI Whisper."""

import io
import tempfile

import numpy as np
import soundfile as sf
import whisper

from app.config import settings

_model: whisper.Whisper | None = None


def _get_model() -> whisper.Whisper:
    global _model
    if _model is None:
        _model = whisper.load_model(settings.whisper_model)
    return _model


def transcribe_audio(audio_bytes: bytes, sample_rate: int = 16000) -> str:
    """Transcribe audio bytes to text using Whisper.

    Args:
        audio_bytes: Raw audio file bytes (WAV, MP3, etc.)
        sample_rate: Sample rate of the audio (used for raw PCM only).

    Returns:
        Transcribed text string.
    """
    model = _get_model()

    # Write audio bytes to a temp file for Whisper
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        # Try to read as an audio file first (WAV, MP3, etc.)
        try:
            audio_data, sr = sf.read(io.BytesIO(audio_bytes))
            # Convert stereo to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            sf.write(tmp.name, audio_data, sr)
        except Exception:
            # Assume raw PCM float32
            audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
            sf.write(tmp.name, audio_data, sample_rate)

        result = model.transcribe(tmp.name, language="en")

    return result["text"].strip()
