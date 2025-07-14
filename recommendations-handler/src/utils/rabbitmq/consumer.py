from typing import Callable

import pika
from loguru import logger
from pika.exceptions import AMQPConnectionError


class RabbitMQConsumer:
    def __init__(self, host: str, queue_name: str, handler: Callable):

        self.host = host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.handler = handler
        self._connect()

    def _connect(self):
        try:
            logger.info(f"Attempting to connect to RabbitMQ at {self.host}...")
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.host)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name)
            logger.success(
                f"Successfully connected and declared queue '{self.queue_name}'."
            )
        except AMQPConnectionError as e:
            logger.error(f"Could not connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
            raise  # TODO: retry mechanism

    def start_consuming(self):
        if not self.channel or not self.connection or self.connection.is_closed:
            logger.warning(
                "Connection lost or not established. Attempting to reconnect..."
            )
            self._connect()

        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.handler,
                auto_ack=True,
            )
            logger.info("Waiting for messages...")
            self.channel.start_consuming()
        except AMQPConnectionError as e:
            logger.error(f"AMQP connection error during consume start: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during consuming: {e}")
        finally:
            self.close()

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ connection closed.")
