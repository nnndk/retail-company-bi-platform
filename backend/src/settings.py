from pydantic import BaseModel, Field

from config.config import Config


class Project(BaseModel):
    """
    Project info
    """

    # Project name
    title: str = 'Retail Company BI Platform'
    # Project description
    description: str = 'Business Intelligence Platform for Retail Companies'
    # Project version
    release_version: str = Field(default='0.1.0')


class Settings:
    """
    Project settings
    """

    # Project info
    project: Project = Project()

    # Host and port of the server project (from config file)
    HOST: str = Config.get_config_item('APP', 'HOST')
    PORT: int = int(Config.get_config_item('APP', 'PORT'))

    # Database connection string (from config file)
    database_url: str = Config.get_config_item('APP', 'DATABASE_URL')


# Settings initialization
settings = Settings()
