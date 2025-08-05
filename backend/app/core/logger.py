import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myservice")


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
