from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from typing import Annotated
import os

from fastapi.params import Body

import routers
from auth.auth_tool import AuthTool
from analytical_tools.excel_db_converter import ExcelDbConverter
from analytical_tools.olap_cube_manager import OlapCubeManager
from db_tools.database import database
from db_tools.services.user_service import UserService


AppRouter = APIRouter(
    prefix=''
)
UPLOAD_DIR = 'temp_storage'


@AppRouter.post('/upload_excel/', status_code=status.HTTP_201_CREATED)
async def upload_excel(token: Annotated[str, Depends(routers.oauth2_scheme)],
                       file: UploadFile = File(...),
                       fact_column_names: list[str] = Body(...)):
    """
    Upload a file to the server
    :param token: Access token for authorization
    :param file: A file
    :param fact_column_names: A list of fact column names
    :return: None
    """
    credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials')
    payload = AuthTool.decode_access_token(token)
    fact_columns: list[str] = list(fact_column_names[0].split(','))

    if payload is None:
        raise credentials_exception

    username: str = payload.get('username')
    user_service: UserService = UserService(database.session)
    user = user_service.get_user_by_username(username)

    # Create the directory if it doesn't exist
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # Save the uploaded file to the directory
    file_path = os.path.join(UPLOAD_DIR, username + '.xlsx')

    with open(file_path, 'wb') as f:
        f.write(await file.read())

    converter = ExcelDbConverter(file_path, fact_columns, user, database.session)
    converter.convert()

    os.remove(file_path)


@AppRouter.get('/get_cube_info/', status_code=status.HTTP_200_OK)
async def get_cube_info(token: Annotated[str, Depends(routers.oauth2_scheme)]) -> dict:
    """
    Get cube info (all dimensions and their values)
    :param token: Access token for authorization
    :return: None
    """
    credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials')
    payload = AuthTool.decode_access_token(token)

    if payload is None:
        raise credentials_exception

    username: str = payload.get('username')
    user_service: UserService = UserService(database.session)
    user = user_service.get_user_by_username(username)

    cube_manager = OlapCubeManager(user, database.session)
    borders = cube_manager.get_date_borders()

    return {'fact': cube_manager.fact_column_name, 'dimensions': cube_manager.get_all_cube_dimension_values(),
            'min_date': borders[0],
            'max_date': borders[1]
            }


@AppRouter.get('/get_cube_data/', status_code=status.HTTP_200_OK)
async def get_cube_data(token: Annotated[str, Depends(routers.oauth2_scheme)], period_group: str = '') -> list[dict]:
    """
    Get cube data
    :param token: Access token for authorization
    :param period_group: Grouping period (day, month, year)
    :return: None
    """
    credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials')
    payload = AuthTool.decode_access_token(token)

    if payload is None:
        raise credentials_exception

    username: str = payload.get('username')
    user_service: UserService = UserService(database.session)
    user = user_service.get_user_by_username(username)

    cube_manager = OlapCubeManager(user, database.session)

    return cube_manager.get_cube(period_group)


@AppRouter.get('/ping/', status_code=status.HTTP_200_OK)
async def ping() -> str:
    """
    Check if the server is available
    """
    return 'Server works'
