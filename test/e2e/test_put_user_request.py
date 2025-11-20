import pytest
import pytest_asyncio
from starlette.testclient import TestClient

from app.models.models import User
from app.testutils.user_utils import UserGenerator
from db.session_manager import SessionManager


class TestPutUserRequest:
    URL = "/users/%d/"

    @pytest.fixture(autouse=True, scope="function")
    def setup(self, client: TestClient, session_manager: SessionManager,
              request_kwargs, asserts_token, asserts_response):
        self.client = client
        self.session_manager = session_manager
        self.request_kwargs = request_kwargs
        self.asserts_token = asserts_token
        self.asserts_response = asserts_response
        yield


    @pytest.mark.asyncio
    @pytest.mark.parametrize("json", [
        {"login": "new_login"},
        {"first_name": "new"},
        {"last_name": "new"},
        {"second_name": "new"},
        {"login": "new_login", "first_name": "new_first_name"},
        {"first_name": "new_first_name", "second_name": "new_second_name", "last_name": "new_last_name"},
        {"login": "new_login", "first_name": "new_first_name", "second_name": "new_second_name", "last_name": "new_last_name"},
    ])
    async def test_with_valid_request_should_success(self, json: dict):
        user_id = await self.save_user()

        self.request_kwargs["url"] = self.URL % user_id
        self.request_kwargs.update(json=json)
        response = self.client.put(**self.request_kwargs)

        assert response.status_code == 200

        async with self.session_manager.start_without_commit() as session_manager:
            user = await session_manager.users.find_by_id(user_id)
            assert user is not None

            resp_data = response.json()
            for attr, value in json.items():
                assert getattr(user, attr) == value
                assert resp_data.get(attr) == value


    @pytest.mark.asyncio
    async def test_with_invalid_user_id_should_return_404(self):
        self.request_kwargs["url"] = self.URL % 9999
        self.request_kwargs.update(json={"login": "new_login"})
        response = self.client.put(**self.request_kwargs)

        self.asserts_response.assert_error_response(response, 404)


    @pytest.mark.asyncio
    async def test_with_invalid_token_should_return_401(self):
        user_id = await self.save_user()

        self.request_kwargs["url"] = self.URL % user_id
        self.request_kwargs["headers"]["X-Api-Key"] = "invalid_token"
        self.request_kwargs.update(json={"login": "new_login"})
        response = self.client.put(**self.request_kwargs)

        self.asserts_response.assert_error_response(response, 401)


    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_json", [
        {},
        {"login": ""},
        {"first_name": ""},
        {"second_name": ""},
        {"last_name": ""},
        {"login": 123},
        {"first_name": 123},
        {"second_name": 123},
        {"last_name": 123},
    ])
    async def test_with_invalid_body_should_return_422_or_400(self, invalid_json: dict):
        user_id = await self.save_user()

        self.request_kwargs["url"] = self.URL % user_id
        self.request_kwargs.update(json=invalid_json)
        response = self.client.put(**self.request_kwargs)

        self.asserts_response.assert_bad_request(response)


    async def save_user(self) -> int:
        async with self.session_manager.start_with_commit() as session_manager:
            user = UserGenerator.generate_user(1)
            saved_user = await session_manager.users.save(user)
            user_id = saved_user.id

        return user_id


