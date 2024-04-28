from contextlib import AbstractContextManager
from typing import Callable, Type
import datetime as dt

from sqlalchemy import and_
from sqlalchemy.orm import Session
from db_tools.models.user_model import User


class UserRepository:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_all(self) -> list[Type[User]]:
        with self.session_factory() as session:
            return session.query(User).all()

    def get_by_id(self, user_id: int) -> Type[User]:
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == user_id, User.is_deleted == False).first()

            return user

    def get_by_username(self, username: str) -> Type[User]:
        print(username)
        with self.session_factory() as session:
            user = session.query(User).filter(User.username == username, User.is_deleted == False).first()

            return user

    def add(self, username: str, hashed_password: str, email: str) -> User:
        with self.session_factory() as session:
            user = User(username=username,
                        hashed_password=hashed_password,
                        email=email,
                        created_date=dt.datetime.now(),
                        last_modified_date=dt.datetime.now())

            session.add(user)
            session.commit()
            session.refresh(user)

            return user

    def delete_by_id(self, user_id: int) -> bool:
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == user_id, User.is_deleted == False).first()

            if user is None:
                return False

            user.is_deleted = True
            session.commit()
            session.refresh(user)

            return True
