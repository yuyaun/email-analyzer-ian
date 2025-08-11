"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  # Override env vars with values from .env file
env = os.getenv("ENV")
app = os.getenv("APP_NAME")
kafka = os.getenv("KAFKA_BOOTSTRAP_SERVERS")


class Settings(BaseSettings):
    """Pydantic model that centralizes application configuration."""

    # Compose topic names as `{ENV}.{object}.{action}`
    # Configure consumer groups as `{ENV}-{APP_NAME}`
    kafka_bootstrap_servers: str = kafka
    kafka_topic: str = f"{env}.generate.created"
    kafka_result_topic: str = f"{env}.generate.result"
    kafka_consumer_group: str = f"{env}-{app}"
    database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/postgres"
    jwt_secret: str = "secret"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    generate_rate_limit: str = "3/minute"


settings = Settings()  # Exposed settings instance
