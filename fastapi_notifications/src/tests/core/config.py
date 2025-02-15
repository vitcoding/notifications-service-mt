from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    service_schema: str = Field(default="http://")
    service_host: str = Field(default="127.0.0.1")
    service_port: int = Field(default=8006)


config = TestConfig()

service_url = (
    f"{config.service_schema}{config.service_host}" f":{config.service_port}"
)
