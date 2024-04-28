from sqlalchemy import Column, String, Boolean
from db_tools.models.base_model import BaseModel
from db_tools import Base
import datetime as dt


# Define model
class User(Base, BaseModel):
    __tablename__ = "user"

    username = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)

    def __init__(self, username: str, hashed_password: str, email: str, created_date: dt.datetime,
                 last_modified_date: dt.datetime):
        self.username = username
        self.hashed_password = hashed_password
        self.email = email
        self.created_date = created_date
        self.last_modified_date = last_modified_date

