"""Database helpers for persisting LLM task results."""

from collections.abc import Iterable

from app.core.database import AsyncSessionLocal
from app.models.magic_task_result import MagicTaskResult


def _to_model(campaign_sn: str, magic_type: str, input_text: str, result: dict) -> MagicTaskResult:
    """Convert raw parameters to a ``MagicTaskResult`` ORM model."""
    return MagicTaskResult(
        campaign_sn=campaign_sn,
        magic_type=magic_type,
        input=input_text,
        result=result,
    )


async def create_magic_task_result(
    campaign_sn: str, magic_type: str, input_text: str, result: dict
):
    """Persist a single LLM task result."""
    if AsyncSessionLocal is None:
        # async engine is unavailable; skip persistence
        return None
    async with AsyncSessionLocal() as db:
        record = _to_model(campaign_sn, magic_type, input_text, result)
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record


async def create_magic_task_results(records: Iterable[dict]) -> None:
    """Persist multiple LLM task results from any iterable of dictionaries."""
    if AsyncSessionLocal is None:
        return None
    async with AsyncSessionLocal() as db:
        db.add_all([
            _to_model(
                campaign_sn=r["campaign_sn"],
                magic_type=r["magic_type"],
                input_text=r["input_text"],
                result=r["result"],
            )
            for r in records
        ])
        await db.commit()

