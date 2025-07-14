import pika
from loguru import logger
from pika.exceptions import AMQPConnectionError
from pydantic import BaseModel

from config import config


class RabbitMQProducer:
    def __init__(self, host: str, queue: str, exchange: str = ""):
        self.host = host
        self.queue = queue
        self.exchange = exchange
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        try:
            logger.info(f"Attempting to connect to RabbitMQ at {self.host}...")
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.host)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue, durable=True)
            logger.success(f"Successfully connected and declared queue '{self.queue}'.")
        except AMQPConnectionError as e:
            logger.error(f"Could not connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
            raise

    def send_message(self, message: BaseModel):
        if not self.channel or not self.connection or self.connection.is_closed:
            logger.warning(
                "Connection lost or not established. Attempting to reconnect..."
            )
            self._connect()

        try:
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.queue,
                body=message.model_dump_json(),
                properties=pika.BasicProperties(
                    content_type="application/json",
                ),
            )
            logger.success(f"Sent message to '{self.queue}'.")

        except AMQPConnectionError as e:
            logger.error(f"AMQP connection error during publish: {e}")
            self.connection = None
            self.channel = None
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during publish: {e}")
            raise

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ connection closed.")


producer = RabbitMQProducer(host=config.rabbitmq.host, queue=config.rabbitmq.queue)
