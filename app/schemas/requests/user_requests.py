from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)
    first_name: str = Field(..., min_length=3, max_length=50)
    last_name: str = Field(..., min_length=3, max_length=50)
    second_name: str = Field(..., min_length=3, max_length=50)
