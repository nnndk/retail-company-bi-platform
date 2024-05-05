from db_tools.database import database
from db_tools.services.user_service import UserService
from excel_tools.excel_converter import ExcelConverter


from itertools import product

# Example usage:
file_path = 'temp_storage/sales_data.xlsx'
database.create_database()
user_service: UserService = UserService(database.session)
user1 = user_service.get_user_by_username('user1')
converter = ExcelConverter(file_path, ['количество'], user1, database.session)
converter.generate_cube()
