"""Kafka 消費者，負責接收訊息並分派處理。"""

import asyncio
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.core.config import settings
from app.mq.handlers.llm_handler import process_llm_task
from app.services.magic_task_result_service import create_magic_task_results
from app.core.logger import log_event

try:  # pragma: no cover - optional dependency
    from aiokafka import AIOKafkaConsumer
except ModuleNotFoundError:  # pragma: no cover - env without Kafka
    AIOKafkaConsumer = None  # type: ignore


async def consume_messages() -> None:
    """Continuously poll Kafka, process task lists in parallel and store results."""
    if AIOKafkaConsumer is None:
        raise RuntimeError("Kafka consumer dependency is not installed")

    log_event("consumer", "connect", {"bootstrap": settings.kafka_bootstrap_servers})

    consumer = AIOKafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await consumer.start()
    await producer.start()
    try:
        async for msg in consumer:
            payload = msg.value.decode("utf-8")
            log_event(
                "consumer", "message_received", {"topic": msg.topic, "value": payload}
            )
            data = json.loads(payload)
            if isinstance(data, dict):
                data_list = [data]
            elif isinstance(data, list):
                data_list = data
            else:
                log_event("consumer", "invalid_payload", {"value": payload})
                continue
            tasks = [process_llm_task(item) for item in data_list]
            results = await asyncio.gather(*tasks)
            await create_magic_task_results(results)
            await producer.send_and_wait(
                settings.kafka_result_topic, json.dumps(results).encode("utf-8")
            )
    finally:
        await consumer.stop()
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(consume_messages())
    
