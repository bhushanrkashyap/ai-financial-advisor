from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Financial Advisor API"
    app_env: str = "development"
    debug: bool = False

    java_engine_url: str = "http://localhost:8081/api/engine/recommend"
    java_engine_timeout_seconds: float = 5.0
    # Toggle calling the external Java recommendation engine. Set to false to
    # force model-only behavior and use internal fallback recommendations.
    java_engine_enabled: bool = True
    prediction_verbose_logs: bool = False


settings = Settings()
