import pytest

from app.models.models import User
from app.testutils.asserts import Asserts
from app.testutils.user_utils import UserGenerator


class TestGetAccessToken:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, client, session_manager, primary_token_str, password_service, settings, request_kwargs):
        self.client = client
        self.session_manager = session_manager
        self.primary_token = primary_token_str
        self.password_service = password_service
        self.settings = settings
        self.asserts = Asserts.from_settings(settings)
        request_kwargs["url"] = "/tokens/"
        yield


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

        self.asserts.assert_error_response(response, 403)


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
        self.asserts.assert_error_response(response, 401)


    @pytest.mark.asyncio
    async def test_with_nonexistent_user_should_fail(self, request_kwargs):
        request = self.get_request_body()

        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)
        self.asserts.assert_error_response(response, 401)


    @classmethod
    def get_request_body(cls) -> dict:
        return {"login": "testuser", "password": "TestPassword123!"}


class TestRefreshAccessToken:
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, client, session_manager, primary_token_str,
              password_service, settings, jwt_token_service, request_kwargs):

        self.client = client
        self.session_manager = session_manager
        self.primary_token = primary_token_str
        self.password_service = password_service
        self.settings = settings
        self.asserts = Asserts.from_settings(settings)
        self.jwt_token_service = jwt_token_service
        request_kwargs["url"] = "/tokens/refresh/"
        yield


    @pytest.mark.asyncio
    async def test_with_valid_should_success(self, request_kwargs):
        user_id = await self.save_user()

        tokens = self.jwt_token_service.generate_tokens(user_id)
        access_token = tokens[0].token
        refresh_token = tokens[1].token

        request = {"refresh_token": refresh_token}
        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)

        assert response.status_code == 200
        body = response.json()
        new_access_token = body.get("token")
        assert new_access_token is not None
        self.asserts.assert_token(user_id, new_access_token, "access")
        assert new_access_token != access_token


    @pytest.mark.asyncio
    async def test_with_invalid_primary_token_should_fail(self, request_kwargs):
        user_id = await self.save_user()

        tokens = self.jwt_token_service.generate_tokens(user_id)
        refresh_token = tokens[1].token

        request = {"refresh_token": refresh_token}
        request_kwargs.pop("headers")
        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)

        self.asserts.assert_error_response(response, 403)


    @pytest.mark.asyncio
    async def test_with_invalid_refresh_token_should_fail(self, request_kwargs):
        request = {"refresh_token": "invalidtoken"}
        request_kwargs.update(json=request)
        response = self.client.post(**request_kwargs)

        assert response.status_code == 400
        assert len(response.json()["detail"]) > 0


    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_request",
    [
        {},
        {"refresh_token": ""},
        {"refresh_token": None},
        {"invalid_field": "some_value"}
    ]
                             )
    async def test_with_invalid_body_should_fail(self, request_kwargs, invalid_request):
        request_kwargs.update(json=invalid_request)
        response = self.client.post(**request_kwargs)

        assert  response.status_code in (400, 422)
        assert len(response.json()["detail"]) > 0

    async def save_user(self) -> int:
        async with self.session_manager.start_with_commit() as session_manager:
            user = UserGenerator.generate_user(1)
            saved_user = await session_manager.users.save(user)
            return saved_user.id


