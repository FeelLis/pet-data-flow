import pymongo
from beanie import Document
from geojson_pydantic import Polygon


class Recommendation(Document):
    id: str = ""
    description: str
    data_type: str
    polygon: Polygon

    class Settings:
        name = "recommendations"
        indexes = [
            [("id", pymongo.TEXT), ("description", pymongo.TEXT)],
            [("polygon", pymongo.GEOSPHERE)],
        ]
