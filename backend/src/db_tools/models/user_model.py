from sqlalchemy import Column, String, Boolean
import datetime as dt

from db_tools.models.base_model import BaseModel
from db_tools import Base


# Define model
class User(Base, BaseModel):
    """
    Model of a user database table
    """
    __tablename__ = "user"

    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)

    def __init__(self, username: str, hashed_password: str, created_date: dt.datetime,
                 last_modified_date: dt.datetime):
        self.username = username
        self.hashed_password = hashed_password
        self.created_date = created_date
        self.last_modified_date = last_modified_date

