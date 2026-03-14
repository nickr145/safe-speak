from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    elevenlabs_api_key: str = ""
    # Kept for backward compatibility; no longer used now that STT uses ElevenLabs
    whisper_model: str | None = None
    # Allow all origins for now so simple HTML files and local dev UIs can call the API.
    cors_origins: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
