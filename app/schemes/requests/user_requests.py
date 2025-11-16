from pydantic import BaseModel, Field

from app.schemes.requests.base import BaseAuthRequest


class CreateUserRequest(BaseAuthRequest):
    first_name: str = Field(..., min_length=3, max_length=50)
    last_name: str = Field(..., min_length=3, max_length=50)
    second_name: str = Field(..., min_length=3, max_length=50)


class PutUserRequest(BaseModel):
    login: str = Field(default=None, min_length=3, max_length=50,)
    first_name: str = Field(default=None, min_length=3, max_length=50)
    last_name: str = Field(default=None, min_length=3, max_length=50)
    second_name: str = Field(default=None, min_length=3, max_length=50)
