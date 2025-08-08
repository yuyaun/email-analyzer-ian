"""SQLAlchemy model for storing LLM task results."""

from sqlalchemy import Column, Integer, String, JSON, Text, DateTime, func
from app.core.database import Base


class MagicTaskResult(Base):
    """ORM model for the ``magic_task_results`` table."""

    __tablename__ = "magic_task_results"

    id = Column(Integer, primary_key=True, index=True)  # Primary key
    campaign_sn = Column(String)  # Campaign identifier
    magic_type = Column(String)  # Task type
    input = Column(Text)  # Original input text
    result = Column(JSON)  # Raw LLM result
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )  # Creation timestamp

