import json
import re
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.config import settings
from backend.services.llm.base import BaseLLMProvider
from backend.utils.logger import logger

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API Provider implementation with retry logic and Demo Mode fallback."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.demo_mode = settings.is_demo_mode()
        self.client = None

        if not self.demo_mode and self.api_key:
            self._init_client()
        else:
            logger.info("GeminiProvider running in DEMO_MODE (Mock responses enabled).")

    def _init_client(self):
        """Initializes Google GenAI client."""
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"GeminiProvider client initialized with model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize google-genai client ({e}). Falling back to DEMO_MODE.")
            self.demo_mode = True

    def health_check(self) -> bool:
        """Verifies Gemini API connectivity or DEMO mode status."""
        if self.demo_mode:
            return True
        try:
            if not self.client:
                return False
            # Lightweight health check prompt
            response = self.generate_text("Respond with 'OK'")
            return "OK" in response or len(response) > 0
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=False,
    )
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Generates plain text response using Gemini API or mock response in Demo mode."""
        if self.demo_mode:
            return f"[DEMO MODE RESPONSE] Mock analysis response for prompt: {prompt[:60]}..."

        try:
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"System Instruction: {system_instruction}\n\nUser Request:\n{prompt}"

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini generate_text error: {e}")
            if self.demo_mode:
                return "[DEMO FALLBACK RESPONSE] Generated due to API exception."
            raise e

    def generate_json(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Generates validated Pydantic object using Gemini API or mock generation."""
        if self.demo_mode:
            return self._generate_mock_json(schema)

        try:
            # Append schema requirement to prompt
            schema_json = json.dumps(schema.model_json_schema(), indent=2)
            formatted_prompt = (
                f"{prompt}\n\n"
                f"CRITICAL REQUIREMENT: Return ONLY valid JSON matching this exact Pydantic JSON schema without markdown block formatting:\n"
                f"{schema_json}"
            )

            raw_response = self.generate_text(formatted_prompt, system_instruction=system_instruction)
            cleaned_json = self._clean_json_string(raw_response)
            parsed = json.loads(cleaned_json)
            return schema.model_validate(parsed)
        except Exception as e:
            logger.error(f"Gemini generate_json parsing error: {e}. Attempting fallback.")
            if settings.DEMO_MODE or not self.api_key:
                return self._generate_mock_json(schema)
            raise e

    def _clean_json_string(self, text: str) -> str:
        """Strips markdown code fence wrappers from raw LLM output."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\n?```$", "", text)
        return text.strip()

    def _generate_mock_json(self, schema: Type[T]) -> T:
        """Generates a dummy/mock instance of schema for DEMO_MODE."""
        dummy_dict = {}
        fields = schema.model_fields
        for name, field in fields.items():
            annotation = field.annotation
            origin = getattr(annotation, "__origin__", None)
            args = getattr(annotation, "__args__", ())

            # Handle Optional / Union types (e.g. Optional[str])
            if origin is not None and type(None) in args:
                non_none_args = [a for a in args if a is not type(None)]
                if non_none_args:
                    annotation = non_none_args[0]
                    origin = getattr(annotation, "__origin__", None)

            # Primitive fallback values
            if annotation == str:
                dummy_dict[name] = f"Sample {name.replace('_', ' ').title()}"
            elif annotation in (int, float):
                dummy_dict[name] = 85.0 if "score" in name or "fit" in name else 1
            elif annotation == bool:
                dummy_dict[name] = True
            elif origin == list:
                dummy_dict[name] = []
            elif origin == dict:
                dummy_dict[name] = {"sample_key": "sample_value"}
            else:
                dummy_dict[name] = f"Sample {name.replace('_', ' ').title()}"
        
        try:
            return schema.model_validate(dummy_dict)
        except Exception:
            return schema.model_construct(**dummy_dict)

