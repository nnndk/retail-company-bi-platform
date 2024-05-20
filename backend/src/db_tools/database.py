from contextlib import contextmanager, AbstractContextManager
from sqlalchemy import create_engine, orm, MetaData, text
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

    def drop_table_starts_with(self, start_text: str):
        metadata = MetaData()
        metadata.reflect(bind=self._engine)

        tables_to_drop = [table for table in metadata.tables if table.startswith(start_text)]

        for table in tables_to_drop:
            metadata.tables[table].drop(self._engine)

            if table in Base.metadata.tables:
                Base.metadata.remove(Base.metadata.tables[table])

    def drop_views_starts_with(self, start_text: str):
        """
        Drop all views that start with a given prefix.
        :param start_text: The prefix of the view names to be dropped.
        """
        with self.session() as session:
            result = session.execute(
                text('SELECT table_name FROM information_schema.views WHERE table_name LIKE :prefix'),
                {'prefix': f'{start_text}%'}
            )
            views_to_drop = [row[0] for row in result]

            for view in views_to_drop:
                session.execute(text(f'DROP VIEW IF EXISTS {view} CASCADE'))

            session.commit()

    def execute_select_sql_query(self, query: str):
        with self._engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()

        return rows

    def get_cube_name_start_with(self, start_text: str) -> str:
        """
        Get db view name (first one) that starts with a given prefix.
        :param start_text: The prefix of the view names to be dropped.
        """
        with self.session() as session:
            result = session.execute(
                text('SELECT table_name FROM information_schema.views WHERE table_name LIKE :prefix'),
                {'prefix': f'{start_text}%'}
            )
            views = [row[0] for row in result]

            for view in views:
                return view

        return ''


# create db interface instance and init database
database = Database(settings.database_url)
database.create_database()
