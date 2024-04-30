from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime, timedelta, timezone
from jose import jwt

from db_tools.services.user_service import UserService
from src.pydantic_models.user_model import User, UserInDB, UserCreds
from src.common_tools.password_tool import PasswordTool
from db_tools.database import database


AuthRouter = APIRouter(
    prefix='/auth'
)

# Dependency to get the current user based on the provided token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


@AuthRouter.post('/create_user', status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreds):
    user_service: UserService = UserService(database.session)
    hashed_password = PasswordTool.get_hash_password(user_data.password)
    user_db = UserInDB(**user_data.dict(), hashed_password=hashed_password)

    return user_service.create_user(user_db.username, user_db.hashed_password)


@AuthRouter.post("/login")
async def login(user_data: UserCreds):
    user_service: UserService = UserService(database.session)
    user = user_service.get_user_by_username(user_data.username)

    if (user is None) or (not PasswordTool.verify_password(user_data.password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "userInfo": user}


@AuthRouter.post('/signup', status_code=status.HTTP_200_OK)
async def create_user(user_data: UserCreds):
    await create_user(user_data)
    return await login(user_data)


@AuthRouter.get("/test/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
