from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status

from app.models.models import User
from app.schemes.requests.user_requests import CreateUserRequest
from app.schemes.responses.user_responses import CreateUserResponse
from app.schemes.schemes import Token
from app.services import jwt_token_service
from app.services.base import BaseDBService
from app.services.jwt_token_service import JWTTokenService, get_jwt_token_service
from app.services.password_service import get_password_service, PasswordService
from db.session_manager import SessionManager, get_session_manager
from settings.settings import Settings, load_settings


class UserRestService(BaseDBService):
    def __init__(self,
                 password_service: PasswordService,
                 session_manager: SessionManager,
                 jwt_token_service: JWTTokenService,
                 settings: Settings):
        super().__init__(session_manager)
        self.jwt_token_service = jwt_token_service
        self.password_service = password_service
        self.settings = settings

    async def create_user(self, request: CreateUserRequest) -> CreateUserResponse:
        async with self.session_manager.start_with_commit() as session_manager:
            hashed_password = self.password_service.hashed(request.password)
            await self.__check_user_or_raise(request.login, hashed_password, session_manager)

            new_user = self.__create_user_obj(request, hashed_password)
            saved_user: User = await session_manager.users.save(new_user)

            resp_kwargs = request.model_dump()
            resp_kwargs["id"] = saved_user.id
            resp_kwargs.pop("password")

            resp_kwargs["access_token"], resp_kwargs["refresh_token"] = self.jwt_token_service.generate_tokens(saved_user.id)

            return CreateUserResponse(**resp_kwargs)


    async def __check_user_or_raise(self, login, hashed_password, session_manager):
        user = await session_manager.users.find_by_login_and_password(
            login, hashed_password
        )

        if user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="User already exists")


    def __create_user_obj(self, request, hashed_password):
        user_kwargs = request.model_dump()
        del user_kwargs["password"]
        user_kwargs["hashed_password"] = hashed_password
        return User(**user_kwargs)


def get_user_rest_service(
        session_manager: SessionManager = Depends(get_session_manager, use_cache=True),
        jwt_token_service: JWTTokenService = Depends(get_jwt_token_service, use_cache=True),
        settings: Settings = Depends(load_settings, use_cache=True),
        password_service: PasswordService = Depends(get_password_service, use_cache=True),
    ) -> UserRestService:

    return UserRestService(password_service, session_manager, jwt_token_service, settings)