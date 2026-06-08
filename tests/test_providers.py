"""
Tests for LLM provider factory and provider implementations.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestProviderFactory:
    """Test provider factory selection logic."""

    def test_factory_returns_ollama_by_default(self):
        with patch.dict("os.environ", {"LLM_PROVIDER": "ollama"}, clear=False):
            from providers.factory import get_provider
            from providers.ollama import OllamaProvider

            provider = get_provider()
            assert isinstance(provider, OllamaProvider)

    def test_factory_returns_opencode_for_opencode(self):
        with patch.dict("os.environ", {
            "LLM_PROVIDER": "opencode",
            "LLM_API_KEY": "test-key",
            "MODEL_NAME": "gpt-4o-mini",
        }, clear=False):
            from providers.factory import get_provider, reset_provider
            reset_provider()

            from providers.opencode import OpenCodeProvider
            provider = get_provider()
            assert isinstance(provider, OpenCodeProvider)

    def test_factory_returns_opencode_for_bigpick(self):
        with patch.dict("os.environ", {
            "LLM_PROVIDER": "bigpick",
            "LLM_API_KEY": "test-key",
        }, clear=False):
            from providers.factory import get_provider, reset_provider
            reset_provider()

            from providers.opencode import OpenCodeProvider
            provider = get_provider()
            assert isinstance(provider, OpenCodeProvider)

    def test_factory_fallback_for_unknown_provider(self):
        with patch.dict("os.environ", {"LLM_PROVIDER": "unknown_provider"}, clear=False):
            from providers.factory import get_provider, reset_provider
            reset_provider()

            from providers.ollama import OllamaProvider
            provider = get_provider()
            assert isinstance(provider, OllamaProvider)


class TestProviderInterface:
    """Test that providers expose the correct interface."""

    def test_ollama_provider_has_name(self):
        from providers.ollama import OllamaProvider
        with patch.dict("os.environ", {"MODEL_NAME": "llama3.2"}, clear=False):
            provider = OllamaProvider()
            assert "ollama" in provider.name
            assert "llama3.2" in provider.name

    def test_opencode_provider_has_name(self):
        from providers.opencode import OpenCodeProvider
        with patch.dict("os.environ", {
            "LLM_API_KEY": "test-key",
            "MODEL_NAME": "gpt-4o-mini",
        }, clear=False):
            provider = OpenCodeProvider()
            assert "gpt-4o-mini" in provider.name

    def test_base_provider_is_abstract(self):
        from providers.base import LLMProvider
        with pytest.raises(TypeError):
            LLMProvider()  # Cannot instantiate abstract class
