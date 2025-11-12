from datetime import timedelta, datetime

import jwt
import pytest
import pytest_asyncio
from httpx import AsyncClient
from starlette.testclient import TestClient

from app.models.models import PrimaryToken
from app.utils.datetime_utils import utcnow, to_utc
from db.session_manager import SessionManager
from settings.settings import Settings


class TestCreateUser:

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, primary_token_str: str, session_manager: SessionManager,
              client: TestClient, settings: Settings):
        self.primary_token = primary_token_str
        self.session_manager = session_manager
        self.client = client
        self.settings = settings
        yield


    @pytest.fixture(scope="function")
    def request_kwargs(self, primary_token_str) -> dict:
        return {"url":"/users/",
                    "headers":{"Content-Type": "application/json",
                               "X-Api-Key": primary_token_str}
                }.copy()


    @pytest.mark.asyncio
    async def test_create_user_should_success(self, request_kwargs: dict):
        request = {
            "login": "test",
            "password": "<PASSWORD>",
            "first_name": "first",
            "last_name": "last",
            "second_name": "second",
        }
        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)

        assert response.status_code == 201
        body = response.json()

        for key in [k for k in request if k != "password"]:
            assert request[key] == body[key]

        access_token = body["access_token"]["token"]
        assert len(access_token) > 3

        refresh_token = body["refresh_token"]["token"]
        assert len(refresh_token) > 3

        async with self.session_manager.start_without_commit() as start:
            users = await start.users.get_all()
            assert len(users) == 1
            user = users[0]

            self.assert_token(user.id, access_token, "access")
            self.assert_token(user.id, refresh_token, "refresh")


    def assert_token(self, user_id, token, type: str):
        payload = jwt.decode(token,
                             self.settings.SECRET_KEY,
                             algorithms=[self.settings.ALGORITHM])
        assert payload["user_id"] == user_id
        assert payload["type"] == type

        if type == "access":
            expired_timedelta = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif type == "refresh":
            expired_timedelta = timedelta(hours=self.settings.REFRESH_TOKEN_EXPIRE_HOURS)
        else:
            raise RuntimeError(f"Unknown token type: {type}")

        exp = to_utc(datetime.fromtimestamp(payload["exp"]))
        assert exp >= utcnow() + expired_timedelta





