from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from typing import Type, Callable

from db_tools.models.user_model import User
from db_tools.repositories.user_repo import UserRepository


class UserService:
    """
    An instance of this class provides an interface to manage data of the database table 'user'
    """
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        """
        Constructor
        :param session_factory: Database session
        """
        user_repository = UserRepository(session_factory)
        self._repository: UserRepository = user_repository

    def get_users(self) -> list[Type[User]]:
        """
        Get all users in the system, except deleted users
        :return: List of users
        """
        return self._repository.get_all()

    def get_user_by_id(self, user_id: int) -> Type[User]:
        """
        Get user of the system by id (only undeleted)
        :param user_id: User id
        :return: User
        """
        return self._repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Type[User]:
        """
        Get user of the system by username (only undeleted)
        :param username: Username
        :return: User
        """
        return self._repository.get_by_username(username)

    def create_user(self, username: str, hashed_password: str) -> User:
        """
        Create new user in the system
        :param username: Username
        :param hashed_password: Hashed password
        :return: Created user
        """
        return self._repository.add(username, hashed_password)

    def delete_user_by_id(self, user_id: int) -> bool:
        """
        Delete user from the system by id
        :param user_id: User id
        :return: If user has been deleted successfully, returns True,
        else returns False (e.g. if there is no user with such id)
        """
        return self._repository.delete_by_id(user_id)

    def delete_user_by_username(self, username: str) -> bool:
        """
        Delete user from the system by username
        :param username: Username
        :return: If user has been deleted successfully, returns True,
        else returns False (e.g. if there is no user with such username)
        """
        return self._repository.delete_by_username(username)
