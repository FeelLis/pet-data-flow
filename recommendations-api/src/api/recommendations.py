import uuid

from config import DataType, config
from fastapi import APIRouter
from geojson_pydantic import Polygon
from geojson_pydantic.types import PolygonCoords
from loguru import logger
from models.recommendation import Recommendation
from pydantic import BaseModel
from utils.rabbitmq.publisher import publisher

router = APIRouter(prefix="/recommendations")


class RecommendationInput(BaseModel):
    description: str
    data_type: str
    coordinates: PolygonCoords


@router.post(path="/one")
async def upload_one_recommendation(
    recommendation_input: RecommendationInput,
) -> str:
    def _find_data_type_by_name(data_type_name: str) -> DataType:
        for data_type_obj in config.data_types:
            if data_type_obj.name == data_type_name:
                return data_type_obj
        raise ValueError(f"{data_type_name} not recognized as valid data type.")

    try:
        recommendation = Recommendation(
            id=str(uuid.uuid4()),
            description=recommendation_input.description,
            data_type=_find_data_type_by_name(recommendation_input.data_type),
            polygon=Polygon(
                type="Polygon", coordinates=recommendation_input.coordinates
            ),
        )
    except ValueError as e:
        logger.exception(e)
        return str(e)

    logger.info(f"Got new recommendation: {recommendation.id}.")
    await publisher.publish(recommendation)

    return "Successfully sent new recommendation to DB."


@router.post(path="/many")
async def upload_many_recommendation(recommendations: list[RecommendationInput]) -> str:
    for recommendation in recommendations:
        await upload_one_recommendation(recommendation)
    return "Successfully sent new recommendations to DB."
