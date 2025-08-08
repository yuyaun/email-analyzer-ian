"""In-memory storage for task results.

This module provides coroutine-safe helpers to save and retrieve
LLM task results that are produced asynchronously.
"""

import asyncio
from typing import Any, Dict, Optional

# Shared dictionary guarded by an asyncio lock
task_results: Dict[str, Any] = {}
task_lock = asyncio.Lock()


async def save_task_result(task_id: str, result: Any) -> None:
    """Persist a task result in memory."""
    async with task_lock:
        task_results[task_id] = result


async def get_task_result(task_id: str) -> Optional[Any]:
    """Retrieve a task result without removing it."""
    async with task_lock:
        return task_results.get(task_id)


async def pop_task_result(task_id: str) -> Optional[Any]:
    """Remove and return a task result if it exists."""
    async with task_lock:
        return task_results.pop(task_id, None)
