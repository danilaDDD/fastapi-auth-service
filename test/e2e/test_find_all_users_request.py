import pytest
from starlette.testclient import TestClient

from app.testutils.user_utils import UserGenerator
from db.session_manager import SessionManager


class TestFindAllUsersRequest:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, client: TestClient, session_manager: SessionManager,
              request_kwargs, asserts_response):
        self.client = client
        self.session_manager = session_manager

        self.request_kwargs = request_kwargs
        self.request_kwargs["url"] = "/users/"

        self.asserts_response = asserts_response
        yield


    @pytest.mark.asyncio
    async def test_with_not_exist_users_should_return_empty_list(self):
        response = self.client.get(**self.request_kwargs)

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 0


    @pytest.mark.asyncio
    async def test_with_exist_users_should_return_not_empty_list(self):
        user_ids = set()
        async with self.session_manager.start_with_commit() as session_manager:
            for i in range(3):
                user = UserGenerator.generate_user(i)
                saved_user = await session_manager.users.save(user)
                user_ids.add(saved_user.id)


        response = self.client.get(**self.request_kwargs)
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 3

        fields = {"id", "login", "first_name", "second_name", "last_name",}
        for user_data in body:
            for field in fields:
                assert user_data.get(field) is not None


    @pytest.mark.asyncio
    async def test_with_invalid_access_token_should_return_401(self):
        self.request_kwargs["headers"]["X-Api-Key"] = "invalid_token"
        response = self.client.get(**self.request_kwargs)

        self.asserts_response.assert_error_response(response, 401)

