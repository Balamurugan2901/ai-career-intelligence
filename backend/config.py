import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables or .env file."""

    # API Keys & LLM Config
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    DEMO_MODE: bool = True

    # Database Settings
    DATABASE_URL: str = "sqlite:///./career_intelligence.db"

    # Execution Limits & Timeouts
    MAX_RESUME_SIZE_MB: int = 10
    LLM_TIMEOUT: int = 30
    LOG_LEVEL: str = "INFO"

    # Services Config
    MARKET_PROVIDER: str = "mock"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def is_demo_mode(self) -> bool:
        """Determines if application is running in DEMO mode."""
        if self.DEMO_MODE:
            return True
        if not self.GEMINI_API_KEY or self.GEMINI_API_KEY == "your_gemini_api_key_here":
            return True
        return False


settings = Settings()
