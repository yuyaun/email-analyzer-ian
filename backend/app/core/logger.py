"""簡易 JSON 格式 logger，記錄系統事件。"""

import logging
import json
from datetime import datetime
import os
APP_NAME = os.getenv("APP_NAME", "myservice")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(APP_NAME)


def log_event(agent: str, event: str, data: dict, level: str = "INFO") -> None:
    """Log an event to terminal and `agent_log.jsonl` using JSON format."""
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "agent": agent,
        "event": event,
        "level": level,
        "data": data,
    }
    logger.log(getattr(logging, level, logging.INFO), json.dumps(entry))
    with open("agent_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
