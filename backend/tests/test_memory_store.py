"""Tests for the in-memory task result store."""

import asyncio

from app.memory_store import get_task_result, pop_task_result, save_task_result


def test_memory_store_roundtrip():
    async def runner():
        await save_task_result("task1", {"value": 1})
        assert await get_task_result("task1") == {"value": 1}
        assert await pop_task_result("task1") == {"value": 1}
        assert await get_task_result("task1") is None

    asyncio.run(runner())
