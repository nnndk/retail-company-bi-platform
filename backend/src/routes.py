from fastapi import FastAPI

from routers.app_router import AppRouter
from routers.auth_router import AuthRouter


def setup_routes(app: FastAPI) -> None:
    """
    Setup API routes
    """
    app.include_router(AppRouter)
    app.include_router(AuthRouter)
