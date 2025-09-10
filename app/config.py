from dotenv import load_dotenv; load_dotenv()

import os
from pydantic import BaseModel, ValidationError


class Settings(BaseModel):
    """Application configuration loaded from environment variables.

    This model centralizes configuration values for the FastAPI
    application, the LLM client, and database connections. It uses
    Pydantic to parse and validate environment variables with sensible
    defaults. Flags are provided to toggle between real external
    services and local in-memory/mocked implementations for testing.
    """

    APP_NAME: str = "LLM Knowledge Extractor"
    API_PREFIX: str = "/api"
    ENV: str = os.getenv("ENV", "dev")

    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: str | None = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_TABLE: str = os.getenv("SUPABASE_TABLE", "analyses")

    USE_MOCK_LLM: bool = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    USE_INMEM_DB: bool = os.getenv("USE_INMEM_DB", "false").lower() == "true"


def get_settings() -> Settings:
    """Instantiate and return application settings.

    If environment variables are invalid, a RuntimeError is raised to
    highlight misconfiguration early in application startup.
    """
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(f"Invalid configuration: {exc}")