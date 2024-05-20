from db_tools.database import database
from db_tools.services.user_service import UserService
from analytical_tools.excel_db_converter import ExcelDbConverter
from analytical_tools.olap_cube_manager import OlapCubeManager


# Example usage:
file_path = 'temp_storage/user1.xlsx'
database.create_database()
user_service: UserService = UserService(database.session)
user1 = user_service.get_user_by_username('user1')
#converter = ExcelDbConverter(file_path, ['количество'], user1, database.session)
#converter.convert()
#print(converter.olap_cube_query)
#converter.create_graphs()

cube_manager = OlapCubeManager(user1, database.session)
print(cube_manager.get_all_cube_dimensions())
print(cube_manager.get_all_cube_dimension_values())
print(cube_manager.get_cube('year')[:10])
print(cube_manager.get_date_borders())
