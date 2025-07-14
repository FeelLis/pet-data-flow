from typing import Self

from geojson_pydantic import Polygon
from pydantic import BaseModel, model_validator

from config import DataType


class Recommendation(BaseModel):
    description: str
    data_type: DataType
    polygon: Polygon

    @model_validator(mode="after")
    def check_data_type(self) -> Self:
        # TODO: check are by data type
        return self
