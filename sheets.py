import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os


load_dotenv()

class GoogleTableManager:
    def __init__(self, creditals_path=".creditals.json"):
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        self.url = os.getenv("SPREADSHEET_NAME")
        self.list_name = os.getenv("LIST_NAME")
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(creditals_path, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = None
        self.spreadsheet = None

    def connect(self):
        self.spreadsheet = self.client.open_by_url(self.url)
        self.sheet = self.spreadsheet.worksheet(self.list_name)
    
    def get_data_of_users(self): 
        #Получить значения с диапазона ячеек 
        bats = {}
        bats['796'] = self.sheet.get_values('B1:B100')
        for i in range(len(bats['796'])):
            bats['796'][i] = bats['796'][i][0]
        return bats
    
    def update_table(self):
        temp_sheet = self.sheet
        self.sheet = self.spreadsheet.worksheet("Состав")
        rows_count = self.sheet.row_count
        cols_count = self.sheet.col_count
        self.sheet.sort((1, 'asc'), range=f'A3:X{rows_count}')
        full_range = f"A1:{gspread.utils.rowcol_to_a1(rows_count, cols_count)}"
        border_style = {
            "style": "SOLID",
            "color": {
                "red": 1.0,
                "green": 1.0,
                "blue": 1.0
            }
        }
        self.sheet.format(full_range, {
            "borders": {
                "top": border_style,
                "bottom": border_style,
                "left": border_style,
                "right": border_style
            }
        })
        self.sheet = temp_sheet
    
    def get_ranks(self):
        ranks = self.sheet.get_values('E1:E100')
        for i in range(len(ranks)):
            ranks[i] = ranks[i][0]
        return ranks
    
    def get_bats(self):
        bats = self.sheet.get_values('F1:F100')
        for i in range(len(bats)):
            bats[i] = bats[i][0]
        return bats
