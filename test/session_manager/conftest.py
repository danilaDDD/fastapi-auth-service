import pytest

from db.connection import session_factory
from db.session_manager import SessionManager


@pytest.fixture(scope="module")
def session_manager() -> SessionManager:
    return SessionManager(session_factory=session_factory)