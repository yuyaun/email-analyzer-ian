"""Tests for the in-memory task result store."""

import asyncio

from app.memory_store import save_task_result, get_task_result_with_lock


def test_memory_store_roundtrip():
    async def runner():
        await save_task_result("task1", {"value": 1})
        assert await get_task_result_with_lock("task1") == {"value": 1}
        # Second retrieval should return None because the result was popped
        assert await get_task_result_with_lock("task1") is None

    asyncio.run(runner())
