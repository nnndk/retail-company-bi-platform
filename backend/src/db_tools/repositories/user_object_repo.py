from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from typing import Callable, Type
import datetime as dt

from db_tools.models.user_object_model import UserObject


class UserObjectRepository:
    """
    An instance of this class allows to interact with user_object db table: create, get, and delete entries
    """
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        """
        Constructor
        :param session_factory: Database session
        """
        self.session_factory = session_factory

    def get_all(self) -> list[Type[UserObject]]:
        """
        Get all user objects from the table 'user_object'
        :return: List of user objects
        """
        # TODO: add pagination
        with self.session_factory() as session:
            return session.query(UserObject).all()

    def get_all_by_owner_username(self, owner_username: str) -> list[Type[UserObject]]:
        """
        Get all objects owned by this user
        :param owner_username: Username of the database table owner
        :return: List of user objects
        """
        with self.session_factory() as session:
            user_objects = session.query(UserObject).filter(UserObject.owner_username == owner_username).all()

            return user_objects

    def get_by_table_name(self, table_name: str) -> Type[UserObject]:
        """
        Get user object by table name
        :param table_name: Name of the database table
        :return: User object
        """
        with self.session_factory() as session:
            user_object = session.query(UserObject).filter(UserObject.table_name == table_name).first()

            return user_object

    def add(self, owner_username: str, table_name: str) -> UserObject:
        """
        Add the entry of new user object to this table
        :param owner_username: Username of the object owner
        :param table_name: Name of the database table
        :return: Add new user object row
        """
        with self.session_factory() as session:
            user_object = UserObject(owner_username=owner_username,
                        table_name=table_name,
                        created_date=dt.datetime.now(),
                        last_modified_date=dt.datetime.now())

            session.add(user_object)
            session.commit()
            session.refresh(user_object)

            return user_object

    def delete_all_by_owner_username(self, owner_username: str) -> bool:
        """
        Delete all rows of this user (when you delete all objects of this user)
        :param owner_username: Username of the object owner
        :return: If rows are deleted successfully, returns True
        """
        with self.session_factory() as session:
            user_objects = session.query(UserObject).filter(UserObject.owner_username == owner_username)

            if user_objects is None:
                return False

            session.delete(user_objects)
            session.commit()

            return True

    def delete_by_table_name(self, table_name: str) -> bool:
        """
        Delete a row with such a table name (when you delete a table from db)
        :param table_name: Name of the database table
        :return: If the row is deleted successfully, returns True
        """
        with self.session_factory() as session:
            user_object = session.query(UserObject).filter(UserObject.table_name == table_name).first()

            if user_object is None:
                return False

            session.delete(user_object)
            session.commit()

            return True
