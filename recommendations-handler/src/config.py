from pydantic import BaseModel

from utils.toml_settings import TomlSettings


class RabbitMQSettings(BaseModel):
    host: str
    exchange: str = ""
    queue: str


class MongoDBSettings(BaseModel):
    url: str


class Config(TomlSettings):
    service_name: str

    mongodb: MongoDBSettings
    rabbitmq: RabbitMQSettings


config = Config()  # type: ignore
