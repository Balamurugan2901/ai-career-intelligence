from typing import Optional, Type, TypeVar
from pydantic import BaseModel

from backend.services.llm.base import BaseLLMProvider
from backend.services.llm.gemini_provider import GeminiProvider
from backend.utils.logger import logger

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """Unified LLM Service layer abstracting underlying AI providers from agents."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.provider = provider or GeminiProvider()
        logger.info(f"LLMService initialized with provider: {self.provider.__class__.__name__}")

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Proxies text generation request to provider."""
        return self.provider.generate_text(prompt, system_instruction=system_instruction)

    def generate_json(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Proxies structured output generation request to provider."""
        return self.provider.generate_json(prompt, schema=schema, system_instruction=system_instruction)

    def is_healthy(self) -> bool:
        """Returns True if provider connection is healthy or in DEMO mode."""
        return self.provider.health_check()


# Singleton instance for easy import across agents
llm_service = LLMService()
