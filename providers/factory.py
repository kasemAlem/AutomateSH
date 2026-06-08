"""
Provider factory — returns the configured LLM provider instance.
Uses lru_cache so the provider is created once and reused.
"""

from functools import lru_cache

from app.config import get_settings
from providers.base import LLMProvider


@lru_cache(maxsize=1)
def get_provider() -> LLMProvider:
    """
    Return the configured LLM provider.

    Selection order from .env LLM_PROVIDER:
        ollama   → OllamaProvider (local, free)
        opencode → OpenCodeProvider (OpenCode API)
        bigpick  → OpenCodeProvider (BigPick, OpenAI-compat)
        openai   → OpenCodeProvider (standard OpenAI)

    Falls back to Ollama if provider is unrecognized.
    """
    settings = get_settings()
    provider_name = settings.llm_provider.strip().lower()

    if provider_name == "ollama":
        from providers.ollama import OllamaProvider
        return OllamaProvider()

    if provider_name in ("opencode", "bigpick", "openai"):
        from providers.opencode import OpenCodeProvider
        return OpenCodeProvider()

    # Default fallback
    from providers.ollama import OllamaProvider
    return OllamaProvider()


def reset_provider() -> None:
    """Clear the cached provider. Useful in tests."""
    get_provider.cache_clear()
