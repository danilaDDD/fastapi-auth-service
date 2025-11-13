import datetime
from email.header import Header

from fastapi import APIRouter, Response, Depends
from starlette import status

from app.routers.base import get_response_modes
from app.schemes.requests.user_requests import CreateUserRequest
from app.schemes.responses.error_responses import ServerErrorResponse, BadRequestResponse, UnauthorizedResponse, \
    ForbiddenResponse
from app.schemes.responses.user_responses import CreateUserResponse
from app.security.api_key import valid_primary_token
from app.services.rest_service import get_user_rest_service, UserRestService

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)
@user_router.post("/",
                  responses={
                        status.HTTP_201_CREATED: {
                            "model": CreateUserResponse,
                            "description": "User created successfully.",
                        },
                }
)
async def create_user(request_body: CreateUserRequest,
                      response: Response,
                      api_key: str = Depends(valid_primary_token),
                      user_rest_service: UserRestService = Depends(get_user_rest_service)) -> CreateUserResponse:
    response.status_code = status.HTTP_201_CREATED
    return await user_rest_service.create_user(request_body)
