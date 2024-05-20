from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError  # python-jose in requirements

from config.config import Config


class AuthTool:
    """
    This class provides some static methods for authentication
    """
    _SECRET_KEY = Config.get_config_item('AUTH', 'SECRET_KEY')
    _ALGORITHM = 'HS256'

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """
        Create an access token for authentication
        :param data: Some user data that will be stored in the token
        :param expires_delta: Access token expiration time (in minutes)
        :return: Access token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=120)

        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, AuthTool._SECRET_KEY, algorithm=AuthTool._ALGORITHM)

        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(token, AuthTool._SECRET_KEY, algorithms=[AuthTool._ALGORITHM])
            return payload
        except JWTError:
            return None
