import datetime

from fastapi import APIRouter, Response, status
from starlette import status

from app.schemas.requests.user_requests import CreateUserRequest
from app.schemas.responses.user_responses import CreateUserResponse
from app.schemas.schemas import Token

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@user_router.post("/")
async def create_user(request: CreateUserRequest, response: Response) -> CreateUserResponse:
    response.status_code = status.HTTP_201_CREATED

    return CreateUserResponse(
        id=1,
        login=request.login,
        first_name=request.first_name,
        last_name=request.last_name,
        second_name=request.second_name,

        access_token=Token(token="access_token_example",
                           expired_at=datetime.datetime.now() + datetime.timedelta(minutes=15)),
        refresh_token=Token(token="refresh_token_example",
                            expired_at=datetime.datetime.now() + datetime.timedelta(days=7)),
    )