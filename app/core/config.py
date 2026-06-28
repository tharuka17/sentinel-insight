from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    VLLM_BASE_URL: str = "http://localhost:8000/v1"
    VLLM_MODEL: str = "meta-llama/Llama-3.1-8B-Instruct"
    OPENAI_API_KEY: str = "not-set"

    # Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sentinel"
    POSTGRES_USER: str = "sentinel"
    POSTGRES_PASSWORD: str = "changeme"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LangSmith
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "sentinel"

    # Slack
    SLACK_WEBHOOK_URL: str = ""

    # App
    LOG_LEVEL: str = "INFO"
    CONFIDENCE_THRESHOLD: float = 0.75
    MAX_WORKERS: int = 4


settings = Settings()
