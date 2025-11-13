import pytest

from app.models.models import User
from app.testutils.asserts import Asserts
from app.testutils.user_utils import UserGenerator


class TestGetAccessToken:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, client, session_manager, primary_token_str, password_service, settings):
        self.client = client
        self.session_manager = session_manager
        self.primary_token = primary_token_str
        self.password_service = password_service
        self.settings = settings
        self.asserts = Asserts(secret_key=settings.SECRET_KEY,
                               algorithm=settings.ALGORITHM,
                               access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                               refresh_token_expire_hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
        yield

    @pytest.fixture(scope="function")
    def request_kwargs(self, primary_token_str) -> dict:
        return {"url":"/tokens/",
                    "headers":{"Content-Type": "application/json",
                               "X-Api-Key": primary_token_str}
                }.copy()


    @pytest.mark.asyncio
    async def test_with_valid_request_should_success(self, request_kwargs):
        request = self.get_request_body()
        hashed_password = self.password_service.hashed(request["password"])

        async with self.session_manager.start_with_commit() as session_manager:
            user = User(
                login=request["login"],
                hashed_password=hashed_password,
                first_name="first",
                second_name="second",
                last_name="last",
            )
            saved_user = await session_manager.users.save(user)
            user_id = saved_user.id

        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)

        assert response.status_code == 200

        body = response.json()
        access_token = body["access_token"]["token"]
        self.asserts.assert_token(user_id, access_token, "access")
        refresh_token = body["refresh_token"]["token"]
        self.asserts.assert_token(user_id, refresh_token, "refresh")


    @pytest.mark.asyncio
    async def test_without_primary_token_should_fail(self, request_kwargs):
        request = self.get_request_body()
        request_kwargs["headers"].pop("X-Api-Key")
        request_kwargs.update(json=request)

        response = self.client.post(**request_kwargs)

        assert response.status_code == 403
        assert len(response.json()["detail"]) > 0


    @pytest.mark.asyncio
    async def test_with_invalid_password_should_fail(self, request_kwargs):
        request = self.get_request_body()
        hashed_another_password = self.password_service.hashed("AnotherPassword!")

        async with self.session_manager.start_with_commit() as session_manager:
            user = User(
                login=request["login"],
                hashed_password=hashed_another_password,
                first_name="first",
                second_name="second",
                last_name="last",
            )
            await session_manager.users.save(user)

        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)
        assert response.status_code == 401
        assert len(response.json()["detail"]) > 0


    @pytest.mark.asyncio
    async def test_with_nonexistent_user_should_fail(self, request_kwargs):
        request = self.get_request_body()

        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)
        assert response.status_code == 401
        assert len(response.json()["detail"]) > 0


    @classmethod
    def get_request_body(cls) -> dict:
        return {"login": "testuser", "password": "TestPassword123!"}
