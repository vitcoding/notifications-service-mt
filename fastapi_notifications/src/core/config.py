import os
from logging import config as logging_config

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

load_dotenv()


class GlobalConfig(BaseSettings):
    """Base configuration settings for the entire application."""

    # the project name for Swagger docs
    project_name: str = Field(default="Notifications")
    base_dir: str = Field(
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


class DBConfig(BaseSettings):
    """Configuration settings for the database."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="postgres_",
        extra="ignore",
    )

    user: str = Field(default="postgres")
    password: str = Field(default="secret")
    db: str = Field(default="auth_db")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=5432)


class CacheConfig(BaseSettings):
    """Configuration settings for the cache storage."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="redis_",
        extra="ignore",
    )

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=6379)


class BrokerConfig(BaseSettings):
    """Configuration settings for the message broker."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="rabbitmq_",
        extra="ignore",
    )

    user: str = Field(default="user")
    password: str = Field(default="secret")
    prefix: str = Field(default="pyamqp")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=5672)

    @property
    def connection(self):
        connection_ = (
            f"{self.prefix}://{self.user}:{self.password}"
            f"@{self.host}:{self.port}"
        )
        return connection_


# logging settings
logging_config.dictConfig(LOGGING)


class Config(BaseSettings):
    """Base configuration settings class."""

    globals: GlobalConfig = GlobalConfig()
    db: DBConfig = DBConfig()
    cache: CacheConfig = CacheConfig()
    broker: BrokerConfig = BrokerConfig()


config = Config()
