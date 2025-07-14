from pydantic import BaseModel, PositiveFloat

from utils.toml_settings import TomlSettings


class DataType(BaseModel):
    name: str
    area_size: PositiveFloat


class Config(TomlSettings):
    service_name: str
    debug_mode: bool

    data_types: list[DataType]


config = Config()  # type: ignore
