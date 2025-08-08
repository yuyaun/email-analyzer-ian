"""專案設定管理，讀取環境變數並提供設定值。"""

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv(override=True)  # Load environment variables from .env file, overriding existing ones
env = os.getenv("ENV")
app = os.getenv("APP_NAME")


class Settings(BaseSettings):
    """集中管理專案設定的 Pydantic 模型。"""

    # 組成 topic 名稱（格式為 `{ENV}.{object}.{action}`）
    # 建立與監控 consumer group（格式為 `{ENV}-{APP_NAME}`）
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = f"{env}.order.created"
    kafka_result_topic: str = f"{env}.order.result"
    kafka_consumer_group: str = f"{env}-{app}"
    database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/postgres"
    jwt_secret: str = "secret"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str = ""


settings = Settings()  # 對外使用的設定實例
