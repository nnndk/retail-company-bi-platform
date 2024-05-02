import uvicorn

from bootstrap import build_app
from settings import settings


if __name__ == '__main__':
    """
    Run the application
    """
    app = build_app()
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)  # run a server of the application
