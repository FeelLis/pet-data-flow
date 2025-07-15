import asyncio
import json

import aio_pika
from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from config import config
from models.recommendation import Recommendation
from utils.rabbitmq.consumer import RabbitMQConsumer


async def handle_recommendation(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            recommendation = Recommendation(
                id=data["id"],
                description=data["description"],
                data_type=data["data_type"]["name"],
                polygon=data["polygon"],
            )
        except Exception as e:
            logger.error(f"Failed to deserialize data: {e}")
            raise

        existing = await Recommendation.find_one(
            {
                "polygon": {
                    "$geoWithin": {"$geometry": recommendation.polygon.model_dump()}
                }
            }
        )
        if existing:
            logger.warning(
                f"Polygon {recommendation.id} is inside polygon {existing.id}, skipping."
            )
        else:
            await recommendation.insert()
            logger.success(f"Inserted polygon {recommendation.id}.")


async def main():
    try:
        logger.info(f"Attempting to connect to MongoDB at {config.mongodb.url}...")
        client = AsyncIOMotorClient(config.mongodb.url)
        await init_beanie(database=client.db_name, document_models=[Recommendation])
        logger.success("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return

    consumer = RabbitMQConsumer(
        url=config.rabbitmq.url,
        queue_name=config.rabbitmq.queue_name,
        handler=handle_recommendation,
    )
    await consumer.connect()
    await consumer.run()


if __name__ == "__main__":
    asyncio.run(main())
