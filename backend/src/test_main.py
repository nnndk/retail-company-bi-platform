from db_tools.database import database
from db_tools.services.user_service import UserService
from excel_tools.excel_converter import ExcelConverter


# Example usage:
file_path = 'temp_storage/user1.xlsx'
database.create_database()
user_service: UserService = UserService(database.session)
user1 = user_service.get_user_by_username('user1')
converter = ExcelConverter(file_path, ['количество'], user1, database.session)
converter.generate_cube()
#print(converter.olap_cube_query)
converter.create_graphs()
