import asyncio

import pika
from beanie import Document, Indexed, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from models.recommendation import Recommendation


def callback(ch, method, properties, body):
    print(f" [x] Received {body}")


async def main():
    client = AsyncIOMotorClient("mongodb://user:pass@host:27017")
    await init_beanie(database=client.db_name, document_models=[Recommendation])

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="hello")

    channel.basic_consume(queue="hello", on_message_callback=callback, auto_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    asyncio.run(main())
