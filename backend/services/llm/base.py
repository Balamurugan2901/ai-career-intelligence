from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract interface for LLM service providers."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Generates plain text response from prompt."""
        pass

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Generates structured Pydantic object response from prompt."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verifies provider connection status."""
        pass
