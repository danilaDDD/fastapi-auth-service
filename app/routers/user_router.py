import datetime
from email.header import Header

from fastapi import APIRouter, Response, status, Depends
from sqlalchemy.sql.annotation import Annotated
from starlette import status

from app.routers.base import get_response_modes
from app.schemes.requests.user_requests import CreateUserRequest
from app.schemes.responses.error_responses import ServerErrorResponse, BadRequestResponse, UnauthorizedResponse, \
    ForbiddenResponse
from app.schemes.responses.user_responses import CreateUserResponse
from app.schemes.schemes import Token
from app.security.api_key import get_api_key

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

create_user_response_models=get_response_modes({
                        status.HTTP_201_CREATED: {
                            "model": CreateUserResponse,
                            "description": "User created successfully.",
                        },
                })
@user_router.post("/",
                  responses=create_user_response_models
)
async def create_user(request: CreateUserRequest,
                      response: Response,
                      api_key: str = Depends(get_api_key)) -> CreateUserResponse:
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