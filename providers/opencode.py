"""
OpenAI-compatible provider.
Works with: OpenAI, OpenCode, BigPick, Groq, Together, Mistral, etc.
Any service that exposes an OpenAI-compatible /chat/completions endpoint.
"""

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.config import get_settings
from providers.base import LLMProvider


class OpenCodeProvider(LLMProvider):
    """
    OpenAI-compatible provider.
    Configure via .env:
        LLM_PROVIDER=opencode
        LLM_API_KEY=your-key
        LLM_BASE_URL=https://opencode.ai/api/v1  (or leave empty for OpenAI)
        MODEL_NAME=gpt-4o-mini
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.llm_api_key or "not-needed"
        self._base_url = settings.llm_base_url  # None = use OpenAI default
        self._model = settings.model_name or "gpt-4o-mini"

    @property
    def name(self) -> str:
        provider = "openai" if not self._base_url else "opencode-compat"
        return f"{provider}/{self._model}"

    def get_llm(self) -> BaseChatModel:
        kwargs: dict = {
            "model": self._model,
            "api_key": self._api_key,
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        if self._base_url:
            kwargs["base_url"] = self._base_url

        return ChatOpenAI(**kwargs)
