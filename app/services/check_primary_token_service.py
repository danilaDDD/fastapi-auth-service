from fastapi import Depends

from app.models.models import PrimaryToken
from app.services.base import BaseDBService
from db.session_manager import SessionManager, get_session_manager


class CheckPrimaryTokenService(BaseDBService):

    async def find_primary_token(self, primary_token: str) -> PrimaryToken | None:
        async with self.session_manager.start_without_commit() as session_manager:
            return await session_manager.primary_tokens.find_by_token(primary_token)


def get_check_primary_token_service(
        session_manager: SessionManager = Depends(get_session_manager, use_cache=True)
                                   ) -> CheckPrimaryTokenService:
    return CheckPrimaryTokenService(session_manager)