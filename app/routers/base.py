from fastapi import status

from app.schemas.responses import error_responses

def get_response_modes(added_responses: dict = None) -> dict:

    response_modes = {
        status.HTTP_400_BAD_REQUEST: {
            "model": error_responses.BadRequestResponse,
            "description": "Bad request. The input data is invalid.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": error_responses.ServerErrorResponse,
            "description": "Internal server error.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": error_responses.UnauthorizedResponse,
            "description": "Unauthorized. Authentication credentials were not provided or are invalid.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": error_responses.ForbiddenResponse,
            "description": "Forbidden. Invalid or missing API key.",
        }
    }

    copy_modes = response_modes.copy()
    if added_responses:
        copy_modes.update(added_responses)

    return copy_modes
