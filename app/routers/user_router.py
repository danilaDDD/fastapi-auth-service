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
from app.services.rest_service import get_user_rest_service, UserRestService

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)
@user_router.post("/",
                  responses=get_response_modes({
                        status.HTTP_201_CREATED: {
                            "model": CreateUserResponse,
                            "description": "User created successfully.",
                        },
                })
)
async def create_user(request: CreateUserRequest,
                      response: Response,
                      api_key: str = Depends(get_api_key),
                      user_rest_service: UserRestService = Depends(get_user_rest_service)) -> CreateUserResponse:

    response.status_code = status.HTTP_201_CREATED

    return await user_rest_service.create_user(request)