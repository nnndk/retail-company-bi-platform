from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Annotated
import os

import routers
from auth.auth_tool import AuthTool


AppRouter = APIRouter(
    prefix=''
)
UPLOAD_DIR = 'temp_storage'


@AppRouter.post('/upload_excel/')
async def upload_excel(token: Annotated[str, Depends(routers.oauth2_scheme)], file: UploadFile = File(...)) -> None:
    """
    Upload a file to the server
    :param token: Access token for authorization
    :file: A file
    :return: None
    """
    credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials')
    payload = AuthTool.decode_access_token(token)

    if payload is None:
        raise credentials_exception

    username: str = payload.get('username')

    # Create the directory if it doesn't exist
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # Save the uploaded file to the directory
    file_path = os.path.join(UPLOAD_DIR, username + '.xlsx')

    with open(file_path, 'wb') as f:
        f.write(await file.read())
