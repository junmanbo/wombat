from fastapi import APIRouter

from app.api.routes import exchanges, login, price_data, private, symbols, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(exchanges.router)
api_router.include_router(symbols.router)
api_router.include_router(price_data.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
