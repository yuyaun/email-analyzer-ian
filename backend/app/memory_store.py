"""Coroutine-safe in-memory store for asynchronous task results."""

import asyncio
from typing import Any, Dict, Optional

# The actual store and its lock
_task_result_store: Dict[str, Any] = {}
_lock = asyncio.Lock()


async def save_task_result(task_id: str, result: Any) -> None:
    """Save a task result into memory in a thread-safe manner."""
    async with _lock:
        _task_result_store[task_id] = result


async def get_task_result_with_lock(task_id: str) -> Optional[Any]:
    """Retrieve and remove a task result atomically."""
    print(f"Retrieving task result for {task_id}, current store len: {len(_task_result_store)}")
    async with _lock:
        return _task_result_store.pop(task_id, None)


# Backward compatible helpers -------------------------------------------------

async def get_task_result(task_id: str) -> Optional[Any]:
    """Retrieve a task result without removing it."""
    async with _lock:
        return _task_result_store.get(task_id)


async def pop_task_result(task_id: str) -> Optional[Any]:
    """Remove and return a task result if it exists."""
    async with _lock:
        return _task_result_store.pop(task_id, None)
