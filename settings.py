# stdlib
from functools import cache

# thirdparty
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        case_sensitive=True,
        extra="ignore",
        env_file_encoding="utf-8",
    )

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    ENV: str = "dev"

    TRACEBACK_OUTPUT_ENABLED: bool = False

    DATABASE_URL: str
    DATABASE_URL_PSYCOPG2: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    ASYNC_ENGINE_POOL_SIZE: int = 20
    ASYNC_ENGINE_MAX_OVERFLOW: int = 50

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    INSTANCES_SOCIAL_ENDPOINT: str = "https://instances.social"
    INSTANCES_SOCIAL_SECRET: str = ""

    MASTODON_INSTANCE_ENDPOINT: str = "https://mastodon.social"
    MASTODON_INSTANCE_ACCESS_TOKEN: str = ""

    OTLP_GRPC_ENDPOINT: str = "http://tempo:4317"
    CHATGPT_API_KEY: str = ""


@cache
def get_settings() -> Settings:
    return Settings()
