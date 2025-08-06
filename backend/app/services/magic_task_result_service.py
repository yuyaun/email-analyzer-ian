from app.core.database import AsyncSessionLocal
from app.models.magic_task_result import MagicTaskResult


async def create_magic_task_result(campaign_sn: str, magic_type: str, result: dict):
    if AsyncSessionLocal is None:
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
