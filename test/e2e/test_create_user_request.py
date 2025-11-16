from datetime import timedelta, datetime

import jwt
import pytest
from starlette.testclient import TestClient

from app.models.models import User
from app.testutils.asserts import AssertsToken
from app.utils.datetime_utils import utcnow, to_utc
from db.session_manager import SessionManager
from settings.settings import Settings


class TestCreateUserRequest:

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, primary_token_str: str, session_manager: SessionManager,
              client: TestClient, settings: Settings,
              password_service, request_kwargs, asserts_token, asserts_response):
        self.primary_token = primary_token_str
        self.session_manager = session_manager
        self.client = client
        self.settings = settings
        self.password_service = password_service
        self.asserts_token = asserts_token
        self.asserts_response = asserts_response
        request_kwargs["url"] = "/users/"
        self.request_kwargs = request_kwargs
        yield


    @pytest.mark.asyncio
    async def test_with_valid_data_should_success(self):
        request = self.get_valid_request_data()
        self.request_kwargs.update(json=request)
        response = self.client.post(**self.request_kwargs)

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

            self.asserts_token.assert_token(user.id, access_token, "access")
            self.asserts_token.assert_token(user.id, refresh_token, "refresh")


    @pytest.mark.asyncio
    async def test_double_request_should_create_should_fail(self):
        request = self.get_valid_request_data()
        self.request_kwargs.update(json=request)
        response1 = self.client.post(**self.request_kwargs)
        response2 = self.client.post(**self.request_kwargs)

        assert response1.status_code == 201
        self.asserts_response.assert_error_response(response2, 400)


    @pytest.mark.asyncio
    async def test_with_existing_login_should_fail(self):
        request = self.get_valid_request_data()

        async with self.session_manager.start_with_commit() as session_manager:
            user_kwargs = request.copy()
            user_kwargs["hashed_password"] = self.password_service.hashed(user_kwargs.pop("password"))
            user = User(**user_kwargs)
            await session_manager.users.save(user)

        self.request_kwargs.update(json=request)
        response = self.client.post(**self.request_kwargs)

        self.asserts_response.assert_error_response(response, 400)


    @pytest.mark.asyncio
    async def test_with_missing_api_key_should_fail(self):
        request = self.get_valid_request_data()
        self.request_kwargs.pop("headers")
        self.request_kwargs.update(json=request)
        response = self.client.post(**self.request_kwargs)

        self.asserts_response.assert_error_response(response, 403)


    @pytest.mark.asyncio
    async def test_with_invalid_api_key_should_fail(self):
        request = self.get_valid_request_data()
        self.request_kwargs["headers"]["X-Api-Key"] = "invalid"
        self.request_kwargs.update(json=request)
        response = self.client.post(**self.request_kwargs)

        self.asserts_response.assert_error_response(response, 401)


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
    async def test_with_invalid_request_should_fail(self, invalid_request: dict):
        self.request_kwargs.update(json=invalid_request)
        response = self.client.post(**self.request_kwargs)

        self.asserts_response.assert_error_response(response, 422)


    def get_valid_request_data(self) -> dict:
        return {
            "login": "test",
            "password": "<PASSWORD>",
            "first_name": "first",
            "last_name": "last",
            "second_name": "second",
        }.copy()



