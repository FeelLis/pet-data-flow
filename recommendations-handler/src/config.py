from typing import Annotated

from pydantic import BaseModel, Field, PositiveFloat

from utils.toml_settings import TomlSettings


class DataType(BaseModel):
    name: str
    area_size: Annotated[tuple[PositiveFloat, PositiveFloat], Field(max_length=2)]


class RabbitMQSettings(BaseModel):
    host: str
    exchange: str = ""
    queue: str


class Config(TomlSettings):
    service_name: str
    debug_mode: bool

    rabbitmq: RabbitMQSettings
    data_types: list[DataType]


config = Config()  # type: ignore
