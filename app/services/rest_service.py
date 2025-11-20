from fastapi import Depends, HTTPException, status

from app.models.models import User
from app.schemas.requests.auth_requests import TokensRequest
from app.schemas.requests.user_requests import CreateUserRequest, PutUserRequest
from app.schemas.responses.token_responses import TokensResponse
from app.schemas.responses.user_responses import CreateUserResponse, UserResponseEntity
from app.schemas.schemas import Token
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


    async def put_user(self, request: PutUserRequest, user_id: int) -> UserResponseEntity:
        async with self.session_manager.start_with_commit() as session_manager:
            source_user = await session_manager.users.find_by_id(user_id)

            if source_user is None:
                raise HTTPException(status_code=404, detail="User not found")

            request_items = request.model_dump().items()

            if len(request_items) == 0:
                raise HTTPException(status_code=400, detail="empty request body")

            for attr, req_value in request_items:
                if req_value:
                    setattr(source_user, attr, req_value)

            saved_user = await session_manager.users.save(source_user)

            return UserResponseEntity.of_user(saved_user)


    async def find_user_by_id(self, user_id: int) -> UserResponseEntity:
        async with self.session_manager.start_without_commit() as session_manager:
            user = await session_manager.users.find_by_id(user_id)

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

            return UserResponseEntity.of_user(user)


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


    async def find_all_users(self) -> list[UserResponseEntity]:
        async with self.session_manager.start_without_commit() as session_manager:
            users = await session_manager.users.get_all()
            return [UserResponseEntity.of_user(u) for u in users]



def get_user_rest_service(
        session_manager: SessionManager = Depends(get_session_manager, use_cache=True),
        jwt_token_service: JWTTokenService = Depends(get_jwt_token_service, use_cache=True),
        settings: Settings = Depends(load_settings, use_cache=True),
        password_service: PasswordService = Depends(get_password_service, use_cache=True),
    ) -> UserRestService:

    return UserRestService(password_service, session_manager, jwt_token_service, settings)


class TokensRestService(BaseDBService):
    def __init__(self,
                 session_manager: SessionManager,
                 jwt_token_service: JWTTokenService,
                 password_service: PasswordService):
        super().__init__(session_manager)
        self.jwt_token_service = jwt_token_service
        self.password_service = password_service


    async def get_tokens(self, request: TokensRequest) -> TokensResponse:

        async with self.session_manager.start_without_commit() as session_manager:
            users = await session_manager.users.find_by_login(request.login)
            users = [u for u in users if self.password_service.verify(request.password, u.hashed_password)]

            if len(users) == 0:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Invalid login or password")

            user = users[0]
            access_token, refresh_token = self.jwt_token_service.generate_tokens(user.id)

            return TokensResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )


    async def refresh_tokens(self, refresh_token: str) -> Token:
        return self.jwt_token_service.refresh_access_token(refresh_token)


def get_tokens_rest_service(
        session_manager: SessionManager = Depends(get_session_manager, use_cache=True),
        jwt_token_service: JWTTokenService = Depends(get_jwt_token_service, use_cache=True),
        password_service: PasswordService = Depends(get_password_service, use_cache=True),
    ) -> TokensRestService:

    return TokensRestService(session_manager, jwt_token_service, password_service)