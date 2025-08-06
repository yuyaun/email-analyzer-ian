from sqlalchemy import Column, Integer, String, JSON
from app.core.database import Base


class MagicTaskResult(Base):
    __tablename__ = "magic_task_results"

    id = Column(Integer, primary_key=True, index=True)
    campaign_sn = Column(String)
    magic_type = Column(String)
    result = Column(JSON)
