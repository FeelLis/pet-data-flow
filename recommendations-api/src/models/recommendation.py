from enum import StrEnum, auto

from geojson_pydantic import Polygon
from pydantic import BaseModel


class DataType(StrEnum):
    pistachios = auto()
    clementines = auto()


class Recommendation(BaseModel):
    description: str
    data_type: DataType
    coordinates: Polygon
