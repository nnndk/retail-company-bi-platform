from pydantic import BaseModel


class User(BaseModel):
    """
    User model
    """
    username: str
    password: str


class UserInDB(User):
    """
    User with a field 'hashed_password' from the db table
    """
    hashed_password: str
