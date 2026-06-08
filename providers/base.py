"""
Abstract base class for all LLM providers.
Every provider must implement this interface so they are interchangeable.
"""

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        ...

    @abstractmethod
    def get_llm(self) -> BaseChatModel:
        """
        Return a LangChain-compatible chat model instance.
        The model is used directly by the pipeline nodes.
        """
        ...

    def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt string.
        Convenience wrapper around get_llm().invoke().
        """
        llm = self.get_llm()
        response = llm.invoke(prompt)
        # Handle both AIMessage and plain string responses
        if hasattr(response, "content"):
            return str(response.content)
        return str(response)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
