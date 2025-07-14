import asyncio

from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from config import config
from models.recommendation import Recommendation
from utils.rabbitmq.consumer import RabbitMQConsumer
from utils.sync_wrapper import sync


@sync
async def handle_recommendation(data: dict):
    recommendation = Recommendation(**data)

    existing = await Recommendation.find_one(
        {"polygon": {"$geoWithin": {"$geometry": recommendation.polygon.model_dump()}}}
    )

    if existing:
        logger.warning(
            f"Polygon {recommendation.id} is inside polygon {existing.id}, skipping."
        )
        return

    await recommendation.insert()
    logger.success(f"Inserted polygon {recommendation.id}.")


async def main():
    client = AsyncIOMotorClient(config.mongodb.url)
    await init_beanie(database=client.db_name, document_models=[Recommendation])

    consumer = RabbitMQConsumer(
        host=config.rabbitmq.host,
        queue=config.rabbitmq.queue,
        handler=handle_recommendation,
    )
    consumer.start_consuming()


if __name__ == "__main__":
    asyncio.run(main())
