from datetime import datetime, timedelta

import jwt

from app.utils.datetime_utils import utcnow, to_utc


class Asserts:
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