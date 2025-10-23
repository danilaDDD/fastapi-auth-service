import os
from typing import Optional

from dotenv import dotenv_values
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.path import get_env_file_path


class Settings(BaseSettings):
    ENV: str
    DB_PREFIX: str
    DB_NAME: str
    DB_USER: str
    DB_HOST: str
    DB_PORT: str
    DB_PASSWORD: str

    def get_database_url(self) -> str:
        return f"{self.DB_PREFIX}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_env_file_path(self) -> str:
        return self.e

    model_config = SettingsConfigDict(
        env_file_encoding = 'utf-8',
    )

def load_settings() -> Settings:
    env = os.getenv('ENV', 'dev')
    env_path = get_env_file_path(env=env)
    env_vars = dotenv_values(env_path)
    env_vars['ENV'] = env
    return Settings(_env_file=env_path, **env_vars)