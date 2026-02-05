from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # =====================================================
    # AWS CONFIG
    # =====================================================
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # =====================================================
    # S3 SETTINGS
    # =====================================================
    S3_BUCKET_NAME: str = "ai-sales-coach-audio"

    S3_AUDIO_PREFIX: str = "audio-uploads/"
    S3_TRANSCRIPT_PREFIX: str = "transcripts/"

    TRANSCRIBE_OUTPUT_BUCKET: str = "ai-sales-coach-audio"
    TRANSCRIBE_JOB_PREFIX: str = "transcribe-job-"

    # =====================================================
    # GROQ / LLM SETTINGS
    # =====================================================
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # =====================================================
    # APP SETTINGS
    # =====================================================
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # =====================================================
    # ENV CONFIG
    # =====================================================
    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }


@lru_cache()
def get_settings():
    return Settings()
