from fastapi import APIRouter

from routes.auth import router as auth_router
from routes.portfolio import router as portfolio_router
from routes.trading import router as trading_router
from routes.forex import router as forex_router
from routes.preferences import router as preferences_router
from routes.news import router as news_router
from routes.insight import router as insight_router

api_router = APIRouter()

api_router.include_router(auth_router,        prefix="/auth",        tags=["auth"])
api_router.include_router(portfolio_router,   prefix="/portfolio",   tags=["portfolio"])
api_router.include_router(trading_router,     prefix="/trade",       tags=["trading"])
api_router.include_router(forex_router,       prefix="/forex",       tags=["forex"])
api_router.include_router(preferences_router, prefix="/preferences", tags=["preferences"])
api_router.include_router(news_router,        prefix="/news",        tags=["news"])
api_router.include_router(insight_router,     prefix="/insight",     tags=["insight"])
