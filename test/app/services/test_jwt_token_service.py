import pytest
from asyncpg.pgproto.pgproto import timedelta
from jwt import InvalidTokenError

from app.services.jwt_token_service import JWTTokenService
from app.utils.datetime_utils import utcnow
from test.conftest import *


class TestJWTTokenService:
    @pytest.fixture(scope="function")
    def jwt_token_service(self, settings: Settings) -> JWTTokenService:
        return JWTTokenService(settings)


    def test_create_valid_access_token_should_successfully(self, jwt_token_service: JWTTokenService, settings: Settings):
        access_token = jwt_token_service.generate_access_token(user_id=3)
        decoded_payload = jwt_token_service.verify_token(access_token, token_type="access")
        now = utcnow()

        assert len(access_token) > 5

        assert decoded_payload is not None
        assert decoded_payload.get("user_id") == 3
        assert decoded_payload.get("exp") <= int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
        assert decoded_payload.get("iat") <= int(now.timestamp())
        assert decoded_payload.get("type") == "access"


    def test_verify_invalid_access_token_should_raise_invalid_token_error(self, settings: Settings):
        jwt_token_service = JWTTokenService(settings)
        invalid_token = "this.is.an.invalid.token"

        with pytest.raises(InvalidTokenError):
            jwt_token_service.verify_token(invalid_token, token_type="access")


    def test_create_valid_refresh_token_should_successfully(self, jwt_token_service: JWTTokenService, settings: Settings):
        refresh_token = jwt_token_service.generate_refresh_token(user_id=5)
        decoded_payload = jwt_token_service.verify_token(refresh_token, token_type="refresh")
        now = utcnow()

        assert len(refresh_token) > 5

        assert decoded_payload is not None
        assert decoded_payload.get("user_id") == 5
        assert decoded_payload.get("exp") <= int((now + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)).timestamp())
        assert decoded_payload.get("iat") <= int(now.timestamp())
        assert decoded_payload.get("type") == "refresh"

    def test_verify_invalid_refresh_token_should_raise_invalid_token_error(self, jwt_token_service: JWTTokenService):
        invalid_token = "this.is.an.invalid.token"
        with pytest.raises(InvalidTokenError):
            jwt_token_service.verify_token(invalid_token, token_type="refresh")


    def test_refresh_access_token_with_valid_refresh_token_should_successfully(self, jwt_token_service: JWTTokenService, settings: Settings):
        refresh_token = jwt_token_service.generate_refresh_token(user_id=10)
        new_access_token = jwt_token_service.refresh_access_token(refresh_token)
        decoded_payload = jwt_token_service.verify_token(new_access_token, token_type="access")
        now = utcnow()

        assert len(new_access_token) > 5

        assert decoded_payload is not None
        assert decoded_payload.get("user_id") == 10
        assert decoded_payload.get("type") == "access"
        assert decoded_payload.get("exp") <= int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
        assert decoded_payload.get("iat") <= int(now.timestamp())