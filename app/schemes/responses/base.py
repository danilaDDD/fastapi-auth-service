from pydantic import BaseModel

from app.schemes.schemes import Token


class BaseTokensResponse(BaseModel):
    access_token: Token
    refresh_token: Token