import os

import pytest

from settings.settings import load_settings, Settings


@pytest.fixture(scope="session", autouse=True)
def setup_all():
    os.environ['ENV'] = 'test'
    yield 


@pytest.fixture(scope="module")
def settings() -> Settings:
    return load_settings()