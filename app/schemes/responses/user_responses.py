from pydantic import BaseModel, ConfigDict

from app.schemes.responses.base import BaseTokensResponse
from app.schemes.schemes import Token


class BaseUserResponse(BaseModel):
    id: int
    login: str
    first_name: str
    last_name: str
    second_name: str

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )


class CreateUserResponse(BaseUserResponse, BaseTokensResponse):
    pass
