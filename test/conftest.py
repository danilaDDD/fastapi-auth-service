import os

import pytest

from app.testutils.asserts import AssertsToken

from app.testutils.asserts import AssertsResponse
from settings.settings import load_settings, Settings


@pytest.fixture(scope="session", autouse=True)
def setup_all():
    os.environ['ENV'] = 'test'
    yield 


@pytest.fixture(scope="module")
def settings() -> Settings:
    return load_settings()

@pytest.fixture(scope="module")
def asserts_token(settings: Settings) -> AssertsToken:
    return AssertsToken.from_settings(settings)


@pytest.fixture(scope="module")
def asserts_response() -> AssertsResponse:
    return AssertsResponse()