"""
Application configuration using Pydantic Settings.
All values can be overridden via environment variables or .env file.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Automate.sh configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM Provider ─────────────────────────────────────────
    llm_provider: str = Field(
        default="ollama",
        description="LLM provider: ollama | opencode | bigpick | openai",
    )
    llm_api_key: str = Field(
        default="not-needed",
        description="API key for cloud LLM providers",
    )
    llm_base_url: str | None = Field(
        default=None,
        description="Base URL for OpenAI-compatible endpoints",
    )
    model_name: str = Field(
        default="llama3.2",
        description="Model name to use for generation",
    )

    # ── Text To Speech ───────────────────────────────────────
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for TTS (and LLM if provider=openai)",
    )
    tts_voice: str = Field(
        default="echo",
        description="OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer)",
    )
    tts_model: str = Field(
        default="tts-1",
        description="OpenAI TTS model (tts-1 or tts-1-hd)",
    )

    # ── Ollama ───────────────────────────────────────────────
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL",
    )

    # ── Database ─────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./automate_sh.db",
        description="SQLAlchemy database URL",
    )

    # ── Quality Control ──────────────────────────────────────
    quality_threshold: int = Field(
        default=7,
        description="Minimum quality score (1-10) to pass quality gate",
        ge=1,
        le=10,
    )
    max_retries: int = Field(
        default=2,
        description="Maximum pipeline retries on quality failure",
        ge=0,
        le=5,
    )

    # ── Output ───────────────────────────────────────────────
    output_dir: str = Field(default="output", description="Directory for generated markdown files")
    content_dir: str = Field(default="content", description="Directory for content assets")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
