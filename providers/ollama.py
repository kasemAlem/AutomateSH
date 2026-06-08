"""
Ollama provider — runs models locally, no API key required.
Install Ollama: https://ollama.ai
Pull a model: ollama pull llama3.2
"""

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama

from app.config import get_settings
from providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Local Ollama LLM provider (free, private, no API key needed)."""

    def __init__(self) -> None:
        settings = get_settings()
        self._model = settings.model_name or "llama3.2"
        self._base_url = settings.ollama_base_url or "http://localhost:11434"

    @property
    def name(self) -> str:
        return f"ollama/{self._model}"

    def get_llm(self) -> BaseChatModel:
        return ChatOllama(
            model=self._model,
            base_url=self._base_url,
            temperature=0.7,
            num_predict=2048,
        )
