from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from typing import Callable, Type
import datetime as dt

from db_tools.models.user_model import User


class UserRepository:
    """
    An instance of this class allows to interact with user db table: create, get, and delete entries
    """
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        """
        Constructor
        :param session_factory: Database session
        """
        self.session_factory = session_factory

    def get_all(self) -> list[Type[User]]:
        """
        Get all users from the table 'user', except deleted users
        :return: List of users
        """
        # TODO: add pagination
        with self.session_factory() as session:
            return session.query(User).all()

    def get_by_id(self, user_id: int) -> Type[User]:
        """
        Get user by id (only undeleted)
        :param user_id: User id
        :return: User
        """
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == user_id, User.is_deleted == False).first()

            return user

    def get_by_username(self, username: str) -> Type[User]:
        """
        Get user by username
        :param username: Username
        :return: User
        """
        with self.session_factory() as session:
            user = session.query(User).filter(User.username == username, User.is_deleted == False).first()

            return user

    def add(self, username: str, hashed_password: str) -> User:
        """
        Add new user to the table 'user'
        :param username: Username
        :param hashed_password: Hashed password
        :return: Created user
        """
        with self.session_factory() as session:
            user = User(username=username,
                        hashed_password=hashed_password,
                        created_date=dt.datetime.now(),
                        last_modified_date=dt.datetime.now())

            session.add(user)
            session.commit()
            session.refresh(user)

            return user

    def delete_by_id(self, user_id: int) -> bool:
        """
        Delete user by id. Actually, it only marks the user as deleted (is_deleted = True)
        :param user_id: User id
        :return: If user has been deleted successfully, returns True,
        else returns False (e.g. if there is no user with such id)
        """
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == user_id, User.is_deleted == False).first()

            if user is None:
                return False

            user.is_deleted = True
            session.commit()
            session.refresh(user)

            return True

    def delete_by_username(self, username: str) -> bool:
        """
        Delete user by username. Actually, it only marks the user as deleted (is_deleted = True)
        :param username: Username
        :return: If user has been deleted successfully, returns True,
        else returns False (e.g. if there is no user with such username)
        """
        with self.session_factory() as session:
            user = session.query(User).filter(User.username == username, User.is_deleted == False).first()

            if user is None:
                return False

            user.is_deleted = True
            session.commit()
            session.refresh(user)

            return True
