from config.config import Config
from pydantic import BaseModel, Field
import os


class Project(BaseModel):
    """
    Описание проекта.
    """

    #: название проекта
    title: str = "Retail Company BI Platform"
    #: описание проекта
    description: str = "Business Intelligence Platform for Retail Companies"
    #: версия релиза
    release_version: str = Field(default="0.1.0")


class Settings:
    """
    Настройки проекта.
    """

    #: описание проекта
    project: Project = Project()

    HOST: str = Config.get_config_item('APP', 'HOST')
    PORT: int = int(Config.get_config_item('APP', 'PORT'))

    #: строка подключения к БД
    database_url: str = Config.get_config_item('APP', 'DATABASE_URL')


# инициализация настроек приложения
settings = Settings()
