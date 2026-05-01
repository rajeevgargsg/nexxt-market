from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://nexxt:nexxtpass@localhost:5432/nexxtmarket"
    redis_url: str = "redis://localhost:6379/0"

    # AI / LLM
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    huggingface_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Search
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_master_key: str = "nexxt_master_key_change_me"

    # Auth
    secret_key: str = "change_me_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080

    # Notifications
    onesignal_app_id: str = ""
    onesignal_api_key: str = ""

    # App
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
