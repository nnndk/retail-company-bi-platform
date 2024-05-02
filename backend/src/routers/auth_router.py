from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated
from datetime import timedelta

from db_tools.services.user_service import UserService
from pydantic_models.user_model import User, UserInDB
from auth.password_tool import PasswordTool
from db_tools.database import database
from auth.auth_tool import AuthTool
import routers


AuthRouter = APIRouter(
    prefix='/auth'
)


@AuthRouter.post('/create_user', status_code=status.HTTP_201_CREATED)
async def create_user(user_data: User):
    """
    Create new user
    :param user_data: User data (username, password, etc)
    :return: Created user
    """
    # TODO: add error raising and handling (existing user etc)
    user_service: UserService = UserService(database.session)
    hashed_password = PasswordTool.get_hash_password(user_data.password)
    user_db = UserInDB(**user_data.dict(), hashed_password=hashed_password)

    return user_service.create_user(user_db.username, user_db.hashed_password)


@AuthRouter.post('/login')
async def login(user_data: User):
    """
    Login
    :param user_data: User data (username, password, etc)
    :return: Dict (json) {'access_token': token, 'token_type': 'token type', 'user_info': user (instance of User)}
    """
    # TODO: add (check) error raising and handling (existing user etc)
    user_service: UserService = UserService(database.session)
    user = user_service.get_user_by_username(user_data.username)

    if (user is None) or (not PasswordTool.verify_password(user_data.password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')

    access_token_expires = timedelta(minutes=routers.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthTool.create_access_token(
        data={'username': user.username}, expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer', 'user_info': {'id': user.id,
                                                                                'username': user.username}}


@AuthRouter.post('/signup', status_code=status.HTTP_200_OK)
async def signup(user_data: User):
    """
    Signup == create user & login
    :param user_data: User data (username, password, etc)
    :return: Same as login(user_data)
    """
    # TODO: add error raising and handling (existing user etc)
    await create_user(user_data)
    return await login(user_data)


@AuthRouter.get('/test/')
async def read_items(token: Annotated[str, Depends(routers.oauth2_scheme)]):
    """
    Login
    :param token: Access token for authorization
    :return: Dict (json) {'token': token}
    """
    # TODO: delete later
    return {'token': token}
