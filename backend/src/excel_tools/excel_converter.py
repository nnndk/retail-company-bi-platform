import pandas as pd
from sqlalchemy import Column, Integer, String, DateTime, inspect
from transliterate import translit
from abc import ABC, abstractmethod
from typing import Type, Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
import time
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

from db_tools import Base
from pydantic_models.user_model import User
from db_tools.database import database
from db_tools.services.user_object_service import UserObjectService


class ExcelConverterABC(ABC):
    """
    An abstract class for converting Excel data into database tables.
    """

    @abstractmethod
    def __init__(self, filename: str, fact_cols: list[str], user: Type[User],
                 session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        """
        Constructor for the abstract ExcelConverter class.

        :param filename: Path to the Excel file.
        :param fact_cols: List of column names containing fact data.
        :param user: User object representing the owner of the data.
        :param session_factory: Factory function to create a session.
        """
        pass

    @abstractmethod
    def generate_cube(self) -> list[dict]:
        """
        Generate dimension and fact tables.
        """
        pass

    @abstractmethod
    def create_graphs(self):
        """
        Create graphs based on group queries.
        """
        pass


class ExcelConverter(ExcelConverterABC):
    """
    A class to convert Excel data into database tables.
    """
    EXCLUDED_COLUMNS = ('#', '№')
    DEFAULT_DIM_COLUMN_VALUE = 'value'
    DEFAULT_DATA_COLUMN_START = 'дата'

    def __init__(self, filename: str, fact_cols: list[str], user: Type[User],
                 session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        """
        Constructor for ExcelConverter class.

        :param filename: Path to the Excel file.
        :param fact_cols: List of column names containing fact data.
        :param user: User object representing the owner of the data.
        :param session_factory: Factory function to create a session.
        """
        self.filename: str = filename
        self.dimension_tables: dict[str, tuple[list[int], list[str], list[type], str]] = {}
        self.fact_column_names: list[str] = []
        self.fact_column_names.extend(fact_cols)
        self.fact_columns: list[list[any]] = []  # [excel_column_name, latin_column_name, excel_column_id] for each fact
        self.user: Type[User] = user
        self.session_factory: Callable[..., AbstractContextManager[Session]] = session_factory
        self.date_column: str = ''
        self.date_column_id: int = -1
        self.latin_date_column = ''
        self.dimension_data: dict[str, dict[str, int]] = {}
        self.main_dim_cols: dict[str, tuple[int, str]] = {}
        self.user_object_service = UserObjectService(session_factory)
        self.dim_table_models = {}
        self.fact_table_name: str = ''
        self.fact_table_model = None
        self.olap_cube_query = ''

        # Load Excel data into DataFrame
        xl = pd.ExcelFile(self.filename)
        sheet_name = xl.sheet_names[0]  # Get the first sheet name
        # Parse the first sheet
        self.df = xl.parse(sheet_name, header=None)
        self._init_dimension_tables()

        date_column = self.df[self.date_column_id - 1][1:]
        date_column = pd.to_datetime(date_column)
        self.min_date = date_column.min()
        self.max_date = date_column.max()

    def _init_dimension_tables(self) -> None:
        """
        Initialize dimension tables from Excel data.
        """
        # Find column ranges for each table
        table_cols = {}

        for col_idx, header in enumerate(self.df.iloc[0], start=1):
            low_header = header.lower()
            if '.' in header:
                table_name, column_name = header.split('.')
            elif low_header in self.fact_column_names:
                latin_fact_col_name = translit(header, 'ru', reversed=True).capitalize()
                self.fact_columns.append([header, latin_fact_col_name, col_idx])
                continue
            elif low_header.startswith(ExcelConverter.DEFAULT_DATA_COLUMN_START) and self.date_column == '':
                self.date_column = header
                self.date_column_id = col_idx
                continue
            elif low_header in ExcelConverter.EXCLUDED_COLUMNS:
                continue
            else:
                table_name = header
                column_name = ExcelConverter.DEFAULT_DIM_COLUMN_VALUE

            column_type = self._infer_column_type(self.df.iloc[1:, col_idx - 1])
            latin_table_name = ExcelConverter._translit(table_name)

            if table_name in table_cols.keys():
                table_cols[table_name][0].append(col_idx)
                table_cols[table_name][1].append(column_name)
                table_cols[table_name][2].append(column_type)
            else:
                table_cols[table_name] = ([col_idx], [column_name], [column_type], latin_table_name)

        self.dimension_tables = table_cols

    def generate_cube(self) -> list[dict]:
        """
        Generate dimension and fact tables.
        """
        database.drop_table_starts_with(f'{self.user.username}_')
        self.user_object_service.delete_all_objects_row_by_owner_username(self.user.username)
        self._generate_dim_tables()
        self._generate_fact_table()
        self._init_olap_cube_query()

        return self._get_olap_cube()

    def _generate_dim_tables(self) -> None:
        """
        Generate dimension tables from Excel data.
        """
        with self.session_factory() as session:
            for table_name, (col_indices, column_names, column_types,
                             latin_table_name) in self.dimension_tables.items():

                db_table_name = f'{self.user.username}_{latin_table_name}'
                database.drop_table(db_table_name)

                # Create a new dimension table in the database
                table_columns = [Column('id', Integer, primary_key=True)]
                table_columns.extend([Column(translit(name, 'ru', reversed=True), col_type,
                                             unique=col_type is String and name != 'id')
                                      for name, col_type in zip(column_names, column_types)])

                table = type(db_table_name, (Base,), {
                    '__tablename__': db_table_name,
                    **{col.name: col for col in table_columns}
                })
                self.dim_table_models[latin_table_name] = table

                Base.metadata.create_all(session.bind)
                self.user_object_service.add_user_object_row(self.user.username, db_table_name)

                self.dimension_data[latin_table_name] = {}
                row_id = -1

                # Store unique values only for string columns
                for main_col_name, main_col_type, main_col_idx in zip(column_names, column_types, col_indices):
                    if main_col_type is String:
                        unique_df = self.df.drop_duplicates(subset=[main_col_idx - 1])

                        for row_idx in range(1, unique_df.shape[0]):
                            values = {}

                            for i in range(len(col_indices)):
                                latin_col_name = ExcelConverter._translit(column_names[i])
                                val = unique_df.iloc[row_idx, col_indices[i] - 1]
                                values[latin_col_name] = val

                                if col_indices[i] == main_col_idx:
                                    row_id += 1
                                    self.dimension_data[latin_table_name][val] = row_id + 1

                            session.add(table(**values))

                        self.main_dim_cols[latin_table_name] = (
                            main_col_idx, translit(main_col_name, 'ru', reversed=True))
                        break
                    else:
                        continue

                session.commit()

    def _generate_fact_table(self) -> None:
        """
        Generate fact table from Excel data.
        """
        start_time = time.time()

        with self.session_factory() as session:
            latin_date_column = translit(self.date_column, 'ru', reversed=True).capitalize()
            self.latin_date_column = latin_date_column
            db_fact_table_name = f'{self.user.username}_facts'
            database.drop_table(db_fact_table_name)
            self.fact_table_name = db_fact_table_name

            # Create a new dimension table in the database
            table_columns = [Column('id', Integer, primary_key=True)]
            table_columns.extend([Column(latin_date_column, DateTime)])
            table_columns.extend([Column(latin_table_name, Integer)
                                  for table_name, (_, _1, _2, latin_table_name) in self.dimension_tables.items()])
            table_columns.extend([Column(translit(col_name, 'ru', reversed=True).capitalize(), Integer)
                                  for col_name in self.fact_column_names])

            table = type(db_fact_table_name, (Base,), {
                '__tablename__': db_fact_table_name,
                **{col.name: col for col in table_columns}
            })
            self.fact_table_model = table

            Base.metadata.create_all(session.bind)
            self.user_object_service.add_user_object_row(self.user.username, db_fact_table_name)
            dimension_data_ids = {}

            for k in self.dimension_data.keys():
                dimension_data_ids[k] = list(self.dimension_data[k].values())

            for i in range(1, self.df.shape[0]):
                values = {}
                date = self.df.at[i, self.date_column_id - 1]
                values[latin_date_column] = date

                for dim_name, (dim_col, _) in self.main_dim_cols.items():
                    dim_value = self.df.at[i, dim_col - 1]
                    values[dim_name] = self.dimension_data[dim_name][dim_value]

                for _, fact_col_name, fact_col_id in self.fact_columns:
                    fact_value = self.df.at[i, fact_col_id - 1]
                    values[fact_col_name] = fact_value

                session.add(table(**values))

            session.commit()
            end_time = time.time()
            print(f'_generate_fact_table process time: {end_time - start_time}')

    def _init_olap_cube_query(self):
        """
        Initialize OLAP cube query.
        """
        display_cols = [f'"{self.latin_date_column}"']

        for fact in self.fact_columns:
            display_cols.append(f'"{fact[1]}"')

        query = ''
        fact_inspector = inspect(self.fact_table_model)
        fact_columns = fact_inspector.columns

        for dim_name, dim_table_model in self.dim_table_models.items():
            dim_table_name = f'"{self.user.username}_{dim_name.capitalize()}"'
            dim_inspector = inspect(dim_table_model)
            dim_columns = dim_inspector.columns

            for fact_column in fact_columns:
                if fact_column.name == dim_name:
                    query += f' JOIN {dim_table_name} ON "{self.fact_table_name}"."{dim_name}" = {dim_table_name}.id'

                    for dim_col in dim_columns:
                        if dim_col.name == ExcelConverter.DEFAULT_DIM_COLUMN_VALUE:
                            display_cols.append(f'{dim_table_name}."{dim_col.name}" AS "{dim_name.capitalize()}"')
                        elif dim_col.name.lower() != 'id':
                            if dim_col.name.lower() == self.main_dim_cols[dim_name][1].lower():
                                display_cols.append(f'{dim_table_name}."{dim_col.name}" AS "{dim_name.capitalize()}"')
                            else:
                                display_cols.append(f'{dim_table_name}."{dim_col.name}" '
                                                    f'AS "{dim_name.capitalize() + "." + dim_col.name.capitalize()}"')
                    break

        base_query = f'SELECT {", ".join(display_cols)} FROM "{self.fact_table_name}"'
        self.olap_cube_query = base_query + query

    def _get_olap_cube(self) -> list[dict]:
        """
        Get OLAP cube data.
        """
        rows = database.execute_select_sql_query(self.olap_cube_query)
        result = []

        for row in rows:
            result.append(row._mapping)

        return result

    def _get_group_queries(self) -> dict[str: str]:
        """
        Get group queries for generating graphs.
        """
        queries = {}

        for dim_name, dim_table_model in self.dim_table_models.items():
            #display_cols = [f'"{self.latin_date_column}"']
            #group_cols = [f'"{self.latin_date_column}"']
            display_cols = []
            group_cols = []

            for fact in self.fact_columns:
                display_cols.append(f'SUM("{fact[1]}")')
                break  # only 1 fact is supported so far

            dim_inspector = inspect(dim_table_model)
            dim_columns = dim_inspector.columns

            for dim_col in dim_columns:
                if dim_col.name == ExcelConverter.DEFAULT_DIM_COLUMN_VALUE:
                    display_cols.append(f'"{dim_name.capitalize()}"')
                    group_cols.append(f'"{dim_name.capitalize()}"')
                elif dim_col.name.lower() != 'id':
                    if dim_col.name.lower() == self.main_dim_cols[dim_name][1].lower():
                        display_cols.append(f'"{dim_name.capitalize()}"')
                        group_cols.append(f'"{dim_name.capitalize()}"')

            query = f'SELECT {", ".join(display_cols)} FROM ({self.olap_cube_query}) GROUP BY {", ".join(group_cols)}'
            queries[dim_name] = query

        return queries

    def create_graphs(self):
        """
        Create graphs based on group queries.
        """
        queries = self._get_group_queries()

        # Initialize an empty list to store the plots
        plots, i = [], 0
        fig, axes = plt.subplots(nrows=len(queries), figsize=(10, 10))

        # Generate plots dynamically
        for dim, query in queries.items():
            data = database.execute_select_sql_query(query)

            values = [entry[0] for entry in data]
            names = [entry[1] for entry in data]

            # Assigning different colors to each bar
            num_colors = len(values)
            colors = plt.cm.viridis(np.linspace(0, 1, num_colors))

            # Plot each bar with a different color
            for j, (value, name) in enumerate(zip(values, names)):
                axes[i].barh(name, value, color=colors[j])

            # Add labels and title
            axes[i].set_title(dim)
            axes[i].set_xlabel(self.fact_columns[0][1])
            axes[i].set_ylabel(dim)

            # Rotate x-axis labels for better readability
            axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45)
            i += 1

        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        # Encode the image as base64
        img_base64 = base64.b64encode(img.getvalue()).decode()

        return """
            <html>
            <head>
                <title>Matplotlib Plots</title>
            </head>
            <body>
                <h1>Matplotlib Plots</h1>
                <div>
                    <h2>Plot 1</h2>
                    <img src="data:image/png;base64,{}" alt="Matplotlib Plot 1">
                </div>
            </body>
            </html>
            """.format(img_base64)

    @staticmethod
    def _infer_column_type(data) -> type:
        """
        Infer the SQLAlchemy column type based on the data in the column.

        :param data: Data to infer type from.
        :return: Type of the data.
        """
        # Check if all values are integers
        if data.astype(str).str.isdigit().all():
            return Integer
        # Check if all values are floats
        else:
            return String

    @staticmethod
    def _translit(text: str) -> str:
        """
        Transliterate Russian text into Latin characters.

        :param text: Russian text to transliterate.
        :return: Transliterated text.
        """
        translit_text = translit(text, 'ru', reversed=True)

        return translit_text.replace("'", '').replace(' ', '_')
