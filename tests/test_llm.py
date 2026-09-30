from pydantic import BaseModel
from backend.services.llm.llm_service import llm_service


class SampleSchema(BaseModel):
    title: str
    fit_score: float
    skills: list[str]


def test_llm_service_health():
    """Verifies LLM service health check returns boolean."""
    assert llm_service.is_healthy() is True


def test_llm_service_generate_text():
    """Verifies text generation using LLM service layer abstraction."""
    text = llm_service.generate_text("Test prompt for backend pipeline")
    assert isinstance(text, str)
    assert len(text) > 0


def test_llm_service_generate_json():
    """Verifies structured JSON validation using LLM service abstraction."""
    result = llm_service.generate_json(
        prompt="Analyze career fit",
        schema=SampleSchema,
    )
    assert isinstance(result, SampleSchema)
    assert hasattr(result, "title")
    assert hasattr(result, "fit_score")
    assert hasattr(result, "skills")
