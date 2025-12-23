from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Bucket(str, Enum):
    IMAGES = "hibistay-images"


class AWSConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AWS_")

    access_key: str
    secret_access_key: str


aws_config = AWSConfig()  # type: ignore
