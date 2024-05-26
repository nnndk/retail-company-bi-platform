import uvicorn

from bootstrap import build_app
from settings import settings
from src.db_tools.database import database


app = build_app()
database.create_database()

if __name__ == '__main__':
    """
    Run the application
    """
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)  # run a server of the application
