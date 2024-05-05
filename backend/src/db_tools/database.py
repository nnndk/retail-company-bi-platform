from contextlib import contextmanager, AbstractContextManager
from sqlalchemy import create_engine, orm, MetaData, Table
from sqlalchemy.orm import Session
from typing import Callable

from db_tools import Base
from settings import settings


class Database:
    """
    An instance of this class allows to manage a database (set in constructor)
    """
    def __init__(self, db_url: str) -> None:
        """
        Constructor
        :param db_url: A database connection string
        """
        self._engine = create_engine(db_url, echo=True)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        """
        Initialize the database by creating all its tables.
        All these tables are models in this project.
        These models are inherited from db_tools.Base (in db_tools.__init__.py)
        :return: None
        """
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        """
        Create a new session of the database. It lets to interact with the database and its tables
        :return: New session
        """
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def drop_table(self, table_name):
        metadata = MetaData()
        metadata.reflect(bind=self._engine)

        if table_name in metadata.tables:
            metadata.tables[table_name].drop(self._engine)


# create db interface instance and init database
database = Database(settings.database_url)
database.create_database()
