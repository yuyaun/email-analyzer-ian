"""Kafka producer wrapper to handle optional dependencies."""

try:  # pragma: no cover - optional dependency
    from aiokafka import AIOKafkaProducer
except ModuleNotFoundError:  # pragma: no cover - env without Kafka
    AIOKafkaProducer = None  # type: ignore


class KafkaProducer:
    """Thin wrapper around :class:`aiokafka.AIOKafkaProducer`."""

    def __init__(self, *args, **kwargs):
        if AIOKafkaProducer is None:
            raise RuntimeError("Kafka producer dependency is not installed")
        self._producer = AIOKafkaProducer(*args, **kwargs)

    async def start(self) -> None:  # pragma: no cover - simple delegation
        await self._producer.start()

    async def stop(self) -> None:  # pragma: no cover - simple delegation
        await self._producer.stop()

    async def send_and_wait(self, *args, **kwargs):  # pragma: no cover - delegation
        return await self._producer.send_and_wait(*args, **kwargs)
