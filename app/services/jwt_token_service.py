import jwt
from typing import Dict, Tuple, Optional, Any
import secrets
from datetime import     timedelta

from fastapi import Depends
from jwt import InvalidTokenError

from app.schemes.schemes import Token
from app.utils.datetime_utils import utcnow
from settings.settings import Settings, load_settings


class JWTTokenService:
    def __init__(self, settings: Settings):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expires = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
        self.settings = settings


    def generate_access_token(self, user_id: int, additional_data: Dict = None) -> Token:
        now = utcnow()
        expired_at = now + self.refresh_token_expires

        payload = {
            'user_id': user_id,
            'type': 'access',
            'exp': expired_at,
            'iat': now,
            'jti': secrets.token_urlsafe(16)  # Unique token ID
        }

        if additional_data:
            payload.update(additional_data)

        return Token(
            token=jwt.encode(payload, self.secret_key, algorithm=self.algorithm),
            expired_at=expired_at,
        )


    def generate_refresh_token(self, user_id: int) -> Token:
        now = utcnow()
        expired_at = now + self.refresh_token_expires

        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': expired_at,
            'iat': now,
            'jti': secrets.token_urlsafe(16)
        }

        return Token(
            token=jwt.encode(payload, self.secret_key, algorithm=self.algorithm),
            expired_at=expired_at
        )

    def generate_tokens(self, user_id: int, additional_data: Dict = None) -> Tuple[Token, Token]:
        access_token = self.generate_access_token(user_id, additional_data)
        refresh_token = self.generate_refresh_token(user_id)

        return access_token, refresh_token

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict]:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

        if payload.get('type') != token_type:
            return None

        return payload


    def refresh_access_token(self, refresh_token: str, additional_data: Dict = None) -> str:
        payload = self.verify_token(refresh_token, "refresh")

        if not payload:
            raise InvalidTokenError("Invalid refresh token")

        user_id = payload.get('user_id')
        new_access_token = self.generate_access_token(user_id, additional_data)

        return new_access_token


def get_jwt_token_service(settings = Depends(load_settings, use_cache=True)) -> JWTTokenService:
    return JWTTokenService(settings)