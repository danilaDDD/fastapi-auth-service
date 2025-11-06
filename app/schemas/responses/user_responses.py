from pydantic import BaseModel, ConfigDict

from app.schemas.schemas import Token


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


class CreateUserResponse(BaseUserResponse):
    access_token: Token
    refresh_token: Token
