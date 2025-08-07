"""SQLAlchemy 模型：儲存 LLM 任務的執行結果。"""

from sqlalchemy import Column, Integer, String, JSON
from app.core.database import Base


class MagicTaskResult(Base):
    """對應 `magic_task_results` 資料表的 ORM 模型。"""

    __tablename__ = "magic_task_results"

    id = Column(Integer, primary_key=True, index=True)  # 自增主鍵
    campaign_sn = Column(String)  # 行銷活動流水號
    magic_type = Column(String)  # 任務類型
    result = Column(JSON)  # LLM 回傳的原始結果

