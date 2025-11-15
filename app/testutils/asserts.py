from datetime import datetime, timedelta

from fastapi import Response
import jwt

from app.utils.datetime_utils import utcnow, to_utc


class Asserts:
    @classmethod
    def from_settings(cls, settings):
        return cls(
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
            access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_hours=settings.REFRESH_TOKEN_EXPIRE_HOURS
        )

    def __init__(self, secret_key: str, algorithm: str,
                 access_token_expire_minutes: int,
                 refresh_token_expire_hours: int):

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_hours = refresh_token_expire_hours


    def assert_token(self, user_id, token, type: str):
        payload = jwt.decode(token,
                             self.secret_key,
                             algorithms=[self.algorithm])
        assert payload["user_id"] == user_id
        assert payload["type"] == type

        if type == "access":
            expired_timedelta = timedelta(minutes=self.access_token_expire_minutes)
        elif type == "refresh":
            expired_timedelta = timedelta(hours=self.refresh_token_expire_hours)
        else:
            raise RuntimeError(f"Unknown token type: {type}")

        exp = to_utc(datetime.fromtimestamp(payload["exp"]))
        assert exp >= utcnow() + expired_timedelta

    def assert_error_response(self, response: Response, expected_status_code):
        assert response.status_code == expected_status_code
        assert len(response.json()["detail"]) > 0