from pydantic_settings import BaseSettings, SettingsConfigDict


class FlagsConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FLAG_")

    development_login: bool


flags_config = FlagsConfig()  # type:ignore
