"""處理 AI 任務結果的資料庫存取。"""

from app.core.database import AsyncSessionLocal
from app.models.magic_task_result import MagicTaskResult


async def create_magic_task_result(campaign_sn: str, magic_type: str, result: dict):
    """將 LLM 任務結果寫入資料庫。"""
    if AsyncSessionLocal is None:
        # 若未安裝 asyncpg 或無法建立非同步引擎，直接跳出
        return
    async with AsyncSessionLocal() as db:
        record = MagicTaskResult(
            campaign_sn=campaign_sn,
            magic_type=magic_type,
            result=result,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

