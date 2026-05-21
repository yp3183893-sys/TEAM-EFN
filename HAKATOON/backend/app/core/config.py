from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://agro:agro_pass@localhost:5432/agrocrm"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    rag_top_k: int = 3
    lead_model_path: str = "app/artifacts/lead_model.joblib"


settings = Settings()
