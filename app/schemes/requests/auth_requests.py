from pydantic import BaseModel

from app.schemes.requests.base import BaseAuthRequest


class TokensRequest(BaseAuthRequest):
    pass


class RefreshTokensRequest(BaseModel):
    refresh_token: str

