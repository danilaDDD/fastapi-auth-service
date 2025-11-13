from datetime import timedelta, datetime

import jwt
import pytest
import pytest_asyncio
from httpx import AsyncClient
from starlette.testclient import TestClient

from app.models.models import PrimaryToken, User
from app.schemes.responses.error_responses import BadRequestResponse
from app.utils.datetime_utils import utcnow, to_utc
from db.session_manager import SessionManager
from settings.settings import Settings


class TestCreateUserRequest:

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, primary_token_str: str, session_manager: SessionManager,
              client: TestClient, settings: Settings, password_service):
        self.primary_token = primary_token_str
        self.session_manager = session_manager
        self.client = client
        self.settings = settings
        self.password_service = password_service
        yield


    @pytest.fixture(scope="function")
    def request_kwargs(self, primary_token_str) -> dict:
        return {"url":"/users/",
                    "headers":{"Content-Type": "application/json",
                               "X-Api-Key": primary_token_str}
                }.copy()


    @pytest.mark.asyncio
    async def test_with_valid_data_should_success(self, request_kwargs: dict):
        request = self.get_valid_request_data()
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

        async with self.session_manager.start_without_commit() as session_manager:
            users = await session_manager.users.get_all()
            assert len(users) == 1
            user = users[0]

            self.assert_token(user.id, access_token, "access")
            self.assert_token(user.id, refresh_token, "refresh")


    @pytest.mark.asyncio
    async def test_double_request_should_create_should_fail(self, request_kwargs: dict):
        request = self.get_valid_request_data()
        request_kwargs.update(json=request)
        response1 = self.client.post(**request_kwargs)
        response2 = self.client.post(**request_kwargs)

        assert response1.status_code == 201
        assert response2.status_code == 400


    @pytest.mark.asyncio
    async def test_with_existing_login_should_fail(self, request_kwargs: dict):
        request = self.get_valid_request_data()

        async with self.session_manager.start_with_commit() as session_manager:
            user_kwargs = request.copy()
            user_kwargs["hashed_password"] = self.password_service.hashed(user_kwargs.pop("password"))
            user = User(**user_kwargs)
            await session_manager.users.save(user)

        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)

        assert response.status_code == 400
        assert len(response.json()["detail"]) > 0


    @pytest.mark.asyncio
    async def test_with_missing_api_key_should_fail(self, request_kwargs: dict):
        request = self.get_valid_request_data()
        request_kwargs.pop("headers")
        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)

        assert response.status_code == 403
        assert len(response.json()["detail"]) > 0


    @pytest.mark.asyncio
    async def test_with_invalid_api_key_should_fail(self, request_kwargs: dict):
        request = self.get_valid_request_data()
        request_kwargs["headers"]["X-Api-Key"] = "invalid"
        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)

        assert response.status_code == 401
        assert len(response.json()["detail"]) > 0


    @pytest.mark.parametrize("invalid_request",
     [
         {},
        {"login": "", "password": "<PASSWORD>", "first_name": "first", "last_name": "last", "second_name": "second"},
        {"login": "test", "password": "", "first_name": "first", "last_name": "last", "second_name": "second"},
        {"login": "test", "password": "<PASSWORD>", "first_name": "", "last_name": "last", "second_name": "second"},
        {"login": "test", "password": "<PASSWORD>", "first_name": "first", "last_name": "", "second_name": "second"},
        {"login": "test", "password": "<PASSWORD>", "first_name": "first", "last_name": "last", "second_name": ""},
        {"login": "login"}, {"password": "<PASSWORD>"}, {"first_name": "first"},
        {"last_name": "last"}, {"second_name": "second"}, {"login": "test", "password": "<PASSWORD>"},
    ])
    @pytest.mark.asyncio
    async def test_with_invalid_request_should_fail(self, request_kwargs: dict, invalid_request: dict):
        request_kwargs.update(json=invalid_request)
        response = self.client.post(**request_kwargs)

        assert response.status_code == 422
        assert len(response.json()["detail"]) > 0


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


    def get_valid_request_data(self) -> dict:
        return {
            "login": "test",
            "password": "<PASSWORD>",
            "first_name": "first",
            "last_name": "last",
            "second_name": "second",
        }.copy()



