from abc import ABC, abstractmethod
from typing import Type, Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from sqlalchemy import text

from pydantic_models.user_model import User
from db_tools.database import database
from db_tools.services.user_object_service import UserObjectService


class OlapCubeManagerABC(ABC):
    @abstractmethod
    def get_date_borders(self) -> tuple[str]:
        pass

    @abstractmethod
    def get_all_cube_dimension_values(self) -> dict[str, list[str]]:
        pass

    @abstractmethod
    def get_cube(self, group_period: str) -> list[dict]:
        pass


class OlapCubeManager(OlapCubeManagerABC):
    def __init__(self, user: Type[User], session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.user = user
        self.session_factory = session_factory
        self.cube_name = database.get_cube_name_start_with(self.user.username)
        self.fact_column_name = self.cube_name[len(f'{self.user.username}_cube_'):].capitalize()
        self.dimensions = self._get_all_cube_dimensions()

    def get_date_borders(self) -> tuple[str, str]:
        query = f'''
            SELECT MIN("Data") AS min_date, MAX("Data") AS max_date 
            FROM {self.cube_name}
        '''
        with self.session_factory() as session:
            result = session.execute(text(query)).one()

        return result.min_date, result.max_date

    def get_all_cube_dimension_values(self) -> dict[str, list[str]]:
        result = {}
        base_query = f'SELECT "value" FROM "{self.user.username}_'

        for dim in self.dimensions:
            query = base_query + dim + '" ORDER BY "value"'
            rows = database.execute_select_sql_query(query)
            result[dim] = []

            for row in rows:
                result[dim].append(row._mapping['value'])

        return result

    def get_cube(self, group_period: str) -> list[dict]:
        if (group_period == 'year') or (group_period == 'month'):
            if group_period == 'year':
                date = 'TO_CHAR("Data", \'YYYY\') AS "Data1"'
            else:
                date = 'TO_CHAR("Data", \'YYYY-MM\') AS "Data1"'

            dims = ', '.join(f'"{item}"' for item in self.dimensions)
            query = (f'SELECT {date}, {dims}, SUM("{self.fact_column_name}") AS "{self.fact_column_name}" '
                     f'FROM {self.cube_name} '
                     f'GROUP BY "Data1", {dims} '
                     f'ORDER BY "Data1"')

            query = f'SELECT "Data1" As "Data", {dims}, "{self.fact_column_name}" FROM ({query})'
            print(query)
        else:
            query = f'SELECT * FROM {self.cube_name}'

        rows = database.execute_select_sql_query(query)
        result = []

        for row in rows:
            result.append(row._mapping)

        return result

    def _get_all_cube_dimensions(self) -> list[str]:
        dimensions = []
        user_obj_service = UserObjectService(self.session_factory)
        objects = user_obj_service.get_all_objects_row_by_owner_username(self.user.username)

        for obj in objects:
            if obj.table_name != f'{self.user.username}_facts':
                dimensions.append(obj.table_name[len(f'{self.user.username}_'):].capitalize())

        return dimensions
