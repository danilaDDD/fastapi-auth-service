from fastapi import APIRouter, status, Response, Depends, HTTPException
from jwt import DecodeError

from app.schemas.requests.auth_requests import TokensRequest, RefreshTokensRequest
from app.schemas.responses.token_responses import TokensResponse
from app.schemas.schemas import Token
from app.security.api_key import valid_primary_token
from app.services.rest_service import get_tokens_rest_service, TokensRestService
from app.utils.datetime_utils import utcnow

auth_router = APIRouter(
    prefix="/tokens",
    tags=["auth"],
)

@auth_router.post("/",
                  responses={
                      status.HTTP_200_OK: {
                          "model": TokensRequest,
                          "description": "Access token generated successfully.",
                      },
                  }
)
async def get_token_access(request: TokensRequest, response: Response,
                           api_key = Depends(valid_primary_token),
                           tokens_rest_service: TokensRestService = Depends(get_tokens_rest_service)) \
        -> TokensResponse:

    response.status_code = status.HTTP_200_OK
    return await tokens_rest_service.get_tokens(request)


@auth_router.post("/refresh",
                  responses={
                      status.HTTP_200_OK: {
                          "model": Token,
                          "description": "Tokens refreshed successfully.",
                      },
                  }
)
async def refresh_tokens(request: RefreshTokensRequest,
                         response: Response,
                         api_key = Depends(valid_primary_token),
                         tokens_rest_service: TokensRestService = Depends(get_tokens_rest_service)) \
        -> Token:
    try:
        response.status_code = status.HTTP_200_OK
        return await tokens_rest_service.refresh_tokens(request.refresh_token)

    except DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
        ) from e
