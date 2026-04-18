import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from datetime import datetime
from db import get_players_data
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

    def get_jedi_prefixes(self):
        jedi_prefixes = self.sheet.get_values('G1:G100')
        for i in range(len(jedi_prefixes)):
            jedi_prefixes[i] = jedi_prefixes[i][0]
        return jedi_prefixes

    def update_data(self, bat_id):
        """
        Обновляет C1:C100 и D1:D100 данными из БД для бойцов из B1:B100.
        Формат ячейки: "<дней_назад> (<часов>)".
        """
        users_by_bat = self.get_data_of_users()
        target_bat_id = str(bat_id)
        rows = []

        # Берем только выбранный батальон и сохраняем порядок бойцов.
        users = users_by_bat.get(target_bat_id, [])
        for nickname in users:
            rows.append((target_bat_id, nickname.strip() if nickname else ""))

        # Гарантируем ровно 100 строк для обновления диапазонов C1:C100 и D1:D100.
        if len(rows) < 100:
            rows.extend([("", "")] * (100 - len(rows)))
        else:
            rows = rows[:100]

        # Запрос только по выбранному батальону.
        cleaned_users = [u for _, u in rows if u]
        server1_data = get_players_data(cleaned_users, server=1, bat_id=target_bat_id)
        server2_data = get_players_data(cleaned_users, server=2, bat_id=target_bat_id)
        today = datetime.now().date()

        def format_value(player_tuple):
            if not player_tuple or player_tuple == (None, None):
                return ""

            date_str, ticks = player_tuple
            if not date_str or ticks is None:
                return ""

            try:
                player_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                days_ago = (today - player_date).days
                hours = round(ticks / 6, 2)
                return f"{days_ago} ({hours})"
            except Exception:
                return ""

        col_c = []
        col_d = []

        for _, nickname in rows:
            if not nickname:
                col_c.append([""])
                col_d.append([""])
                continue

            col_c.append([format_value(server1_data.get(nickname, (None, None)))])
            col_d.append([format_value(server2_data.get(nickname, (None, None)))])

        self.sheet.update(values=col_c, range_name='C1:C100')
        self.sheet.update(values=col_d, range_name='D1:D100')
    
    