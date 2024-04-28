from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    password: str


class UserInDB(User):
    hashed_password: str


class LoginUserData(BaseModel):
    username: str
    password: str
