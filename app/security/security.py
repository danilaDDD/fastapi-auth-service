from fastapi import Security, Depends
from fastapi.security import APIKeyHeader

from app.services.check_primary_token_service import CheckPrimaryTokenService, get_check_primary_token_service

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

async def valid_primary_token(api_key: str = Security(api_key_header),
                              check_primary_token_service: CheckPrimaryTokenService = Depends(get_check_primary_token_service)
                              ) -> str:

    if not await check_primary_token_service.find_primary_token(api_key):
        from fastapi import HTTPException
        from starlette.status import HTTP_401_UNAUTHORIZED

        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    return api_key