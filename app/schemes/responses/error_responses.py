from pydantic import BaseModel


class ServerErrorResponse(BaseModel):
    message: str = "Internal Server Error"
    code: int = 500


class BadRequestResponse(BaseModel):
    message: str = "Bad Request"
    code: int = 400


class NotFoundResponse(BaseModel):
    message: str = "Not Found"
    code: int = 404


class UnauthorizedResponse(BaseModel):
    message: str = "Unauthorized"
    code: int = 401


class ForbiddenResponse(BaseModel):
    message: str = "Forbidden"
    code: int = 403