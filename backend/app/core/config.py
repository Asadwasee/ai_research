from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Research & Report Generation Agent"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    FRONTEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Gemini LLM Settings
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.8-flash"
    
    # Research Tools Configuration
    TAVILY_API_KEY: str | None = None
    TAVILY_MAX_RESULTS: int = 5
    RESEARCH_TOOL_TIMEOUT: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()