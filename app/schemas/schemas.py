from datetime import datetime

from pydantic import BaseModel, Field

class Token(BaseModel):
    token: str = Field(..., min_length=10)
    expired_at: datetime
