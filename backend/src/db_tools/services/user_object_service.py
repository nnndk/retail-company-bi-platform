from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from typing import Type, Callable

from db_tools.models.user_object_model import UserObject
from db_tools.repositories.user_object_repo import UserObjectRepository


class UserService:
    """
    An instance of this class provides an interface to manage data of the database table 'user_object'
    """
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        """
        Constructor
        :param session_factory: Database session
        """
        user_object_repository = UserObjectRepository(session_factory)
        self._repository: UserObjectRepository = user_object_repository

    def get_user_objects(self) -> list[Type[UserObject]]:
        """
        Get all user objects from the table 'user_object'
        :return: List of all user objects
        """
        return self._repository.get_all()

    def get_all_objects_row_by_owner_username(self, owner_username: str) -> list[Type[UserObject]]:
        """
        Get all objects owned by this user
        :param owner_username: Username of the database table owner
        :return: List of user objects
        """
        return self._repository.get_all_by_owner_username(owner_username)

    def get_object_row_by_table_name(self, table_name: str) -> Type[UserObject]:
        """
        Get user object by table name
        :param table_name: Name of the database table
        :return: User
        """
        return self._repository.get_by_table_name(table_name)

    def add_user_object_row(self, owner_username: str, table_name: str) -> UserObject:
        """
        Add the entry of new user object to this table
        :param owner_username: Username of the object owner
        :param table_name: Name of the database table
        :return: Add new user object row
        """
        return self._repository.add(owner_username, table_name)

    def delete_all_objects_row_by_owner_username(self, owner_username: str) -> bool:
        """
        Delete all rows of this user (when you delete all objects of this user)
        :param owner_username: Username of the object owner
        :return: If rows are deleted successfully, returns True
        """
        return self._repository.delete_all_by_owner_username(owner_username)

    def delete_object_row_by_table_name(self, table_name: str) -> bool:
        """
        Delete a row with such a table name (when you delete a table from db)
        :param table_name: Name of the database table
        :return: If the row is deleted successfully, returns True
        """
        return self._repository.delete_by_table_name(table_name)
