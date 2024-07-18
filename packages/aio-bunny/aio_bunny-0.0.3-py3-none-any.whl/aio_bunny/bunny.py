import asyncio
import functools
from typing import Callable, Optional, TypeAlias, TypeVar, List, Dict

import aio_pika
from aio_pika.abc import AbstractConnection

from .consumer import Consumer
from .exchange_types import RabbitExchangeType


Arguments: TypeAlias = Dict[str, str | int | None]
T = TypeVar("T")


class Bunny:
    _conn: AbstractConnection

    def __init__(self, amqp_url: str) -> None:
        self.url = amqp_url

        self._consumers: List[Consumer] = []

    async def _connect(self) -> AbstractConnection:
        return await aio_pika.connect_robust(self.url)

    async def start(self) -> None:
        self._conn = await self._connect()

        await asyncio.gather(
            *[handler.start(self._conn) for handler in self._consumers])

    async def stop(self, timeout: int = None, nowait: bool = False) -> None:
        await asyncio.gather(
            *[consumer.stop(timeout=timeout, nowait=nowait)
                for consumer in self._consumers])

    def consumer(
        self,
        queue: str,
        exchange: str,
        exchange_type: RabbitExchangeType = RabbitExchangeType.DIRECT,
        routing_key: Optional[str] = None,
        prefetch_count: Optional[int] = None,
        auto_ack: bool = False,
        consumer_arguments: Optional[Arguments] = None,

        queue_durable: bool = False,
        queue_auto_delete: bool = False,
        queue_passive: bool = False,
        queue_exclusive: bool = False,
        queue_arguments: Optional[Arguments] = None,

        exchange_durable: bool = False,
        exchange_auto_delete: bool = False,
        exchange_internal: bool = False,
        exchange_passive: bool = False,
        exchange_arguments: Optional[Arguments] = None,
    ) -> Callable:
        def decorator(func: Callable[[bytes], T]) -> Callable:
            self._consumers.append(
                Consumer(
                    func,
                    queue,
                    exchange,
                    exchange_type,
                    routing_key or exchange,
                    prefetch_count=prefetch_count,
                    auto_ack=auto_ack,
                    arguments=consumer_arguments,

                    queue_durable=queue_durable,
                    queue_auto_delete=queue_auto_delete,
                    queue_passive=queue_passive,
                    queue_exclusive=queue_exclusive,
                    queue_arguments=queue_arguments,

                    exchange_durable=exchange_durable,
                    exchange_auto_delete=exchange_auto_delete,
                    exchange_internal=exchange_internal,
                    exchange_passive=exchange_passive,
                    exchange_arguments=exchange_arguments))

            @functools.wraps(func)
            def _decorator(msg: bytes) -> T:
                return func(msg)

            return _decorator
        return decorator
