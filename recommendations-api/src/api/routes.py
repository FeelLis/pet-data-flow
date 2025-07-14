import uuid

from fastapi import APIRouter
from geojson_pydantic import Polygon
from geojson_pydantic.types import PolygonCoords
from loguru import logger

from config import DataType, config
from models.recommendation import Recommendation
from utils.rabbitmq.producer import producer

router = APIRouter(prefix="/recommendations")


def _find_data_type_by_name(data_type_name: str) -> DataType:
    for data_type_obj in config.data_types:
        if data_type_obj.name == data_type_name:
            return data_type_obj
    raise ValueError(f"{data_type_name} not recognized as valid data type.")


@router.post(path="/one")
def upload_one_recommendation(
    description: str,
    data_type: str,
    coordinates: PolygonCoords,
):
    try:
        recommendation = Recommendation(
            id=str(uuid.uuid4()),
            description=description,
            data_type=_find_data_type_by_name(data_type),
            polygon=Polygon(type="Polygon", coordinates=coordinates),
        )
    except ValueError as e:
        logger.exception(e)
        return str(e)

    logger.info(f"Got new recommendation: {recommendation.id}.")
    producer.send_message(recommendation)

    return "Successfully sent new recommendation to DB."
