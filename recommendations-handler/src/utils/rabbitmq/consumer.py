from typing import Callable

import aio_pika
from loguru import logger
from pika.exceptions import AMQPConnectionError


class RabbitMQConsumer:
    def __init__(self, url: str, queue_name: str, handler: Callable):
        self.url = url
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.queue = None
        self.handler = handler

    async def connect(self):
        try:
            logger.info(f"Attempting to connect to RabbitMQ at {self.url}...")
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            self.queue = await self.channel.declare_queue(name=self.queue_name)
            logger.success(
                f"Successfully connected and declared queue '{self.queue_name}'."
            )
        except AMQPConnectionError as e:
            logger.error(f"Could not connect to RabbitMQ: {e}")
            raise  # TODO: retry mechanism

    async def run(self):
        while (
            self.channel
            and self.connection
            and not self.connection.is_closed
            and self.queue
        ):
            try:
                await self.queue.consume(self.handler)
            except AMQPConnectionError as e:
                logger.error(f"AMQP connection error during consume start: {e}")
                break
            except Exception as e:
                logger.exception(f"An unexpected error occurred during consuming: {e}")
        await self.close()

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ connection closed.")
