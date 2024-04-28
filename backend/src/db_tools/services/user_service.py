from typing import Type, Callable
from db_tools.models.user_model import User
from db_tools.repositories.user_repo import UserRepository
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session


class UserService:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        user_repository = UserRepository(session_factory)
        self._repository: UserRepository = user_repository

    def get_users(self) -> list[Type[User]]:
        return self._repository.get_all()

    def get_user_by_id(self, user_id: int) -> Type[User]:
        return self._repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Type[User]:
        return self._repository.get_by_username(username)

    def create_user(self, username: str, hashed_password: str, email: str = '') -> User:
        return self._repository.add(username, hashed_password, email)

    def delete_user_by_id(self, user_id: int) -> bool:
        return self._repository.delete_by_id(user_id)
