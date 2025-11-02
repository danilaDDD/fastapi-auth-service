import asyncio
import os

import pytest

from settings.settings import Settings, load_settings


@pytest.fixture(scope="session", autouse=True)
def setup():
    os.environ['ENV'] = 'test'
    yield 


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()