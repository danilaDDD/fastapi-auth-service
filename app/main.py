from fastapi import FastAPI

from app.middlewares.logging_middleware import LoggingMiddleware
from app.routers.auth_router import auth_router
from app.routers.user_router import user_router
from app.logging import initialize_logger
app = FastAPI()
app.include_router(user_router)
app.include_router(auth_router)

app.add_middleware(LoggingMiddleware)

@app.on_event("startup")
async def startup_event():
    initialize_logger(app)

