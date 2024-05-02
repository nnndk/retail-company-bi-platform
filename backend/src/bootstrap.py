from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import setup_routes


def build_app() -> FastAPI:
    """
    Initializing the FastAPI application and configuring all necessary parameters
    """
    app = FastAPI()
    setup_routes(app)
    origins = ['http://localhost:3000', 'http://127.0.0.1:3000']

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    return app
