from fastapi import APIRouter, status, Response, Depends

from app.schemes.requests.auth_requests import TokensRequest
from app.schemes.responses.token_responses import TokensResponse
from app.schemes.schemes import Token
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
