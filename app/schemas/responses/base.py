from pydantic import BaseModel

from app.schemas.schemas import Token


class BaseTokensResponse(BaseModel):
    access_token: Token
    refresh_token: Token