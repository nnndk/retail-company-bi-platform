from sqlalchemy import Column, String, Integer

from db_tools.models.base_model import BaseModel
from db_tools import Base


# Define model
class UserObject(Base, BaseModel):
    """
    Model of a user database table
    """
    __tablename__ = 'user_object'

    owner_username = Column(String)
    table_name = Column(String)
