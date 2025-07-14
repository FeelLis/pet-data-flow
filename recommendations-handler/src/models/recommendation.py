from typing import Self

import pymongo
from beanie import Document, Go, Indexed
from geojson_pydantic import Polygon

from config import DataType


class Recommendation(Document):
    description: str
    data_type: DataType
    polygon: Polygon

    class Collection:
        name = "recommendations"
        indexes = [
            [("id", pymongo.TEXT), ("description", pymongo.TEXT)],
            [("polygon", pymongo.GEOSPHERE)],
        ]

    class Config:
        schema_extra = {
            "example": {
                "id": "123",
                "description": "Test",
                "data_type": "type",
                "polygon": {
                    "type": "Polygon",
                    "coordinates": [
                        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]
                    ],
                },
            }
        }
