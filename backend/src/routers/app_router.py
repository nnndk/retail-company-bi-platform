from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Annotated
import os

from fastapi.params import Body

import routers
from auth.auth_tool import AuthTool
from excel_tools.excel_converter import ExcelConverter
from db_tools.database import database
from db_tools.services.user_service import UserService


AppRouter = APIRouter(
    prefix=''
)
UPLOAD_DIR = 'temp_storage'


@AppRouter.post('/upload_excel/')
async def upload_excel(token: Annotated[str, Depends(routers.oauth2_scheme)],
                       file: UploadFile = File(...),
                       fact_column_names: list[str] = Body(...)) -> None:
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

    converter = ExcelConverter(file_path, fact_columns, user, database.session)
    converter.generate_cube()
