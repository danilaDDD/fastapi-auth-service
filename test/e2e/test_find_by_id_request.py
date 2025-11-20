import pytest
from starlette.testclient import TestClient

from app.testutils.user_utils import UserGenerator
from db.session_manager import SessionManager


@pytest.mark.e2e
class TestFindByIdRequest:
    URL = "/users/%d/"

    @pytest.fixture(autouse=True, scope="function")
    def setup(self, client: TestClient, session_manager: SessionManager,
              request_kwargs, asserts_response):
        self.client = client
        self.session_manager = session_manager
        self.request_kwargs = request_kwargs
        self.asserts_response = asserts_response
        yield


    @pytest.mark.asyncio
    async def test_with_exist_user_should_success(self):
        user_id = await self.save_user()
        self.set_url(user_id)
        response = self.client.get(**self.request_kwargs)

        assert response.status_code == 200
        self.asserts_response.assert_user_body(response, user_id)

    @pytest.mark.asyncio
    async def test_with_non_exist_user_should_return_404(self):
        self.set_url(9999)

        response = self.client.get(**self.request_kwargs)

        self.asserts_response.assert_error_response(response, 404)


    @pytest.mark.asyncio
    async def test_with_invalid_access_token_should_return_401(self):
        self.request_kwargs["headers"]["X-Api-Key"] = "invalid_token"
        self.set_url(1)
        response = self.client.get(**self.request_kwargs)
        self.asserts_response.assert_error_response(response, 401)


    async def save_user(self) -> int:
        async with self.session_manager.start_with_commit() as session_manager:
            user = UserGenerator.generate_user(1)
            saved_user = await session_manager.users.save(user)
            user_id = saved_user.id

        return user_id

    def set_url(self, user_id):
        self.request_kwargs["url"] = self.URL % user_id
