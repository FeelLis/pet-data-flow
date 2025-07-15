import json
from functools import lru_cache
from typing import Callable, get_type_hints

import aio_pika
from loguru import logger
from pika.exceptions import AMQPConnectionError
from pydantic import BaseModel, ValidationError


class RabbitMQConsumer:
    def __init__(self, url: str, queue_name: str, handler: Callable):
        self.url = url
        self.queue_name = queue_name
        self.handler = handler

    @staticmethod
    @lru_cache(maxsize=None)
    def _get_func_parsed_model_type(func: Callable) -> type[BaseModel]:
        type_hints = get_type_hints(func, include_extras=True)
        for param_type in type_hints.values():
            if issubclass(param_type, BaseModel):
                return param_type
        raise TypeError(
            f"Could not find an argument which is a subclass of {BaseModel.__name__} in function {func.__qualname__}."
        )

    def _deserialize(self, message) -> BaseModel | None:
        data = json.loads(message.body.decode())
        model_type = RabbitMQConsumer._get_func_parsed_model_type(self.handler)
        try:
            return model_type.model_validate(data)
        except ValidationError as e:
            logger.error(
                f"Failed to deserialize RabbitMQ message to model. "
                f"Message data: {data}, Model type: {model_type.__name__}, Error: {e}"
            )
            return None

    async def _connect(self):
        try:
            logger.info(f"Attempting to connect to RabbitMQ at {self.url}...")
            self.connection = await aio_pika.connect_robust(self.url)
            logger.success(f"Connected and declared queue '{self.queue_name}'.")

        except AMQPConnectionError as e:
            logger.error(f"Could not connect to RabbitMQ: {e}")
            raise  # TODO: retry mechanism

    async def _consume(self):
        async with self.connection:
            channel = await self.connection.channel()
            queue = await channel.declare_queue(self.queue_name)
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        data = self._deserialize(message)
                        if data:
                            await self.handler(data)  # TODO: handler can be sync.

    async def run(self):
        await self._connect()
        await self._consume()
