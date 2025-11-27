import datetime
from email.header import Header

from fastapi import APIRouter, Response, Depends
from starlette import status

from app.routers.base import get_response_modes
from app.schemas.requests.user_requests import CreateUserRequest, PutUserRequest
from app.schemas.responses.error_responses import ServerErrorResponse, BadRequestResponse, UnauthorizedResponse, \
    ForbiddenResponse
from app.schemas.responses.user_responses import CreateUserResponse, UserResponseEntity
from app.security.security import valid_primary_token
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


@user_router.put("/{id}/",
                 responses={
                     status.HTTP_200_OK: {
                         "model": UserResponseEntity,
                         "description": "User update successfully."
                     }
                 })
async def edit_user(request: PutUserRequest, id: int,
                    api_key: str = Depends(valid_primary_token),
                    user_rest_service: UserRestService = Depends(get_user_rest_service)) -> UserResponseEntity:

    return await user_rest_service.put_user(request, id)


@user_router.get("/{id}/",
                 responses={
                     status.HTTP_200_OK: {
                         "model": UserResponseEntity,
                         "description": "User retrieved successfully."
                     }
                 })
async def get_user(id: int,
                   api_key: str = Depends(valid_primary_token),
                   user_rest_service: UserRestService = Depends(get_user_rest_service)) -> UserResponseEntity:
    return await user_rest_service.find_user_by_id(id)


@user_router.get("/",
                 responses={
                     status.HTTP_200_OK: {
                         "model": list[UserResponseEntity],
                         "description": "Users retrieved successfully."
                     }
                 })
async def get_all_users(api_key: str = Depends(valid_primary_token),
                            user_rest_service: UserRestService = Depends(get_user_rest_service)) -> list[UserResponseEntity]:
    return await user_rest_service.find_all_users()


