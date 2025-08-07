"""Kafka 消費者，負責接收訊息並分派處理。"""

import asyncio
import json
from confluent_kafka import Consumer
from app.core.config import settings
from app.mq.handlers.llm_handler import process_llm_task
from app.services.magic_task_result_service import create_magic_task_results
from app.core.logger import log_event


conf = {
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "group.id": settings.kafka_consumer_group,
    "auto.offset.reset": "earliest",
}  # Kafka 連線與消費者設定


async def consume_messages() -> None:
    """Continuously poll Kafka, process task lists in parallel and store results."""

    log_event("consumer", "connect", {"bootstrap": settings.kafka_bootstrap_servers})

    consumer = Consumer(conf)
    consumer.subscribe([settings.kafka_topic])

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            await asyncio.sleep(0)
            continue
        if msg.error():
            log_event(
                "consumer", "error", {"error": str(msg.error())}, level="ERROR"
            )
            continue
        payload = msg.value().decode("utf-8")
        log_event("consumer", "message_received", {"topic": msg.topic(), "value": payload})
        data_list = json.loads(payload)
        tasks = [process_llm_task(item) for item in data_list]
        results = await asyncio.gather(*tasks)
        await create_magic_task_results(results)


if __name__ == "__main__":
    asyncio.run(consume_messages())
    
