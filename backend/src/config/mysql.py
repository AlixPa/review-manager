from pydantic_settings import BaseSettings, SettingsConfigDict


class MysqlConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYSQL_")

    database: str
    user_reader: str
    user_writer: str
    password_reader: str
    password_writer: str
    port: int
    host: str


mysql_config = MysqlConfig()  # type: ignore
