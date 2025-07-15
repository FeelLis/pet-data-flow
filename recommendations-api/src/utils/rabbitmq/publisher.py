import aio_pika
from loguru import logger
from pika.exceptions import AMQPConnectionError
from pydantic import BaseModel

from config import config


class RabbitMQPublisher:
    def __init__(self, url: str, queue_name: str):
        self.url = url
        self.queue_name = queue_name

    async def __aenter__(self):
        try:
            logger.info(f"Attempting to connect to RabbitMQ at {self.url}...")
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            await self.channel.declare_queue(self.queue_name)
            logger.success(
                f"Successfully connected and declared queue '{self.queue_name}'."
            )
        except AMQPConnectionError as e:
            logger.error(f"Could not connect to RabbitMQ: {e}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ connection closed.")

    async def publish(self, message: BaseModel):
        if not self.channel or not self.connection or self.connection.is_closed:
            logger.error("Connection lost or not established.")
            return

        try:
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=message.model_dump_json().encode()),
                routing_key=self.queue_name,
            )
            logger.success(f"Sent message to '{self.queue_name}'.")

        except AMQPConnectionError as e:
            logger.error(f"AMQP connection error during publish: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during publish: {e}")
            raise


publisher = RabbitMQPublisher(
    url=config.rabbitmq.url, queue_name=config.rabbitmq.queue_name
)
