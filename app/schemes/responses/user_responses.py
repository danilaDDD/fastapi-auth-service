from pydantic import BaseModel, ConfigDict

from app.models.models import User
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


class UserResponseEntity(BaseUserResponse):

    @classmethod
    def of_user(cls, user: User) -> "UserResponseEntity":
        return cls(
            id=user.id,
            login=user.login,
            first_name=user.first_name,
            last_name=user.last_name,
            second_name=user.second_name
        )
