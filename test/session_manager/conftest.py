from typing import Type

import pytest

from db.session_manager import SessionManager
from test.session_manager.mock import SessionFactoryMock


@pytest.fixture(scope="module")
def test_session_factory() -> Type[SessionFactoryMock]:
    return SessionFactoryMock


@pytest.fixture(scope="module")
def session_manager(test_session_factory) -> SessionManager:
    return SessionManager(session_factory=test_session_factory)