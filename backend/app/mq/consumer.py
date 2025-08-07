import asyncio
from confluent_kafka import Consumer
from app.core.config import settings
from app.mq.handlers.llm_handler import handle_llm_task
from app.core.logger import log_event

conf = {
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "group.id": settings.kafka_consumer_group,
    "auto.offset.reset": "earliest"
}

log_event("consumer", "connect", {"bootstrap": settings.kafka_bootstrap_servers})

consumer = Consumer(conf)
consumer.subscribe([settings.kafka_topic])

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        log_event("consumer", "error", {"error": str(msg.error())}, level="ERROR")
        continue
    log_event("consumer", "message_received", {"topic": msg.topic(), "value": msg.value().decode("utf-8")})
    asyncio.run(handle_llm_task(msg.value().decode("utf-8")))
    
