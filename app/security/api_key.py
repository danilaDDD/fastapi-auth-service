from fastapi import Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):

    return api_key