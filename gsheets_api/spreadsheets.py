import gspread
from google.oauth2.service_account import Credentials


# выносим всё что нам понадобится для работы в гугл таблицей в отдельный класс
class Spreadsheet:
    def __init__(self, sheet_id: str, scopes: list, auth_file: str):

        # передаём данные для подключения
        credentials = Credentials.from_service_account_file(auth_file, scopes=scopes)
        self.client = gspread.authorize(credentials)

        # переходим к таблице
        self.table = self.client.open_by_key(sheet_id)
        # словарь с названиями листов в таблице
        self.sheets = {str(name).split()[1].replace("'", ""): int(str(name).split()[2].split(':')[1].split('>')[0])
                       for name in self.table.worksheets()}
        # дефолтный рабочий лист
        self.default_sheet = self.table.sheet1

    # функция для переключения рабочего листа по его айди
    def current_sheet(self, sheet_id: int):
        return self.table.get_worksheet_by_id(sheet_id)

    # добавление листа
    def add_sheet(self, sheet_name: str) -> None:
        self.table.add_worksheet(title=sheet_name, rows="100", cols="20")

    # копирование листа
    def duplicate_sheet(self, sheet_id: int, new_sheet_name: str) -> None:
        self.table.duplicate_sheet(source_sheet_id=sheet_id, new_sheet_name=f'{new_sheet_name}_copy')

    # добавление строки
    def add_row(self, work_sheet_name: str, row: str) -> None:
        self.table.worksheet(work_sheet_name).append_row(row.split(','))

    # получение списка словарей
    # {шапка: значение}
    def get_all_records_by_rows(self, work_sheet_name: str):
        return self.table.worksheet(work_sheet_name).get_all_records()

    # удаление листа
    def delete_sheet(self, sheet_id: int) -> None:
        self.table.del_worksheet_by_id(sheet_id)
