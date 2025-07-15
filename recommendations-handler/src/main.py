import asyncio

from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from config import config
from models.recommendation import Recommendation
from utils.rabbitmq.consumer import RabbitMQConsumer


async def handle_recommendation(recommendation: Recommendation):
    logger.info(f"Got new recommendation: {recommendation.id}")
    existing = await Recommendation.find_one(
        {"polygon": {"$geoWithin": {"$geometry": recommendation.polygon.model_dump()}}}
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
        logger.success("Connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return

    consumer = RabbitMQConsumer(
        url=config.rabbitmq.url,
        queue_name=config.rabbitmq.queue_name,
        handler=handle_recommendation,
    )
    await consumer.run()


if __name__ == "__main__":
    asyncio.run(main())
