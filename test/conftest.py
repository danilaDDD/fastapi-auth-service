import os

import pytest

from settings.settings import Settings


@pytest.fixture(scope="session", autouse=True)
def setup():
    os.environ['ENV'] = 'test'
    yield 


@pytest.fixture(scope="session")
def settings() -> 'Settings':
    from settings.settings import load_settings
    return load_settings()