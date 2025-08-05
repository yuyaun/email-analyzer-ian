from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv(override=True)  # Load environment variables from .env file, overriding existing ones
env = os.getenv("ENV")
app = os.getenv("APP_NAME")

class Settings(BaseSettings):
    # 組成 topic 名稱（格式為 `{ENV}.{object}.{action}`）
    # 建立與監控 consumer group（格式為 `{ENV}-{APP_NAME}`）
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = f"{env}.order.created"
    kafka_consumer_group: str = f"{env}-{app}"
    database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/postgres"

settings = Settings()