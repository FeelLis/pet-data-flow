from typing import Self

from geojson_pydantic import Polygon
from pydantic import BaseModel, model_serializer, model_validator
from shapely import Polygon as ShapelyPolygon

from config import DataType


class Recommendation(BaseModel):
    id: str
    description: str
    data_type: DataType
    polygon: Polygon

    @model_serializer(when_used="json")
    def serialize_data_type(self) -> dict:
        data = self.model_dump()
        data["data_type"] = self.data_type.name
        return data

    @model_validator(mode="after")
    def check_data_type(self) -> Self:
        area = ShapelyPolygon(
            shell=self.polygon.coordinates[0],
            holes=(
                self.polygon.coordinates[1:]
                if len(self.polygon.coordinates) > 1
                else None
            ),
        ).area

        if not self.data_type.area_size[0] <= area <= self.data_type.area_size[1]:
            raise ValueError(
                f"Incorrect area size ({area}) for this data type ({self.data_type.name})."
            )

        return self
