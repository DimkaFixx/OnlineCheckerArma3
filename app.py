from parcedata import Parser, Bats
from sheets import GoogleTableManager
from db import update_bats_data, get_players_data
import time
from datetime import datetime, timezone, timedelta

MSK_TZ = timezone(timedelta(hours=3))

def main():
    sheets_manager = GoogleTableManager()
    sheets_manager.connect()
    parser = Parser()

    last_table_update_minute = None
    last_full_update_minute = None

    sheets_manager.update_table()
    last_table_update_minute = now.minute
    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} | Форматирование таблицы", flush=True)

    while True:
        now = datetime.now(MSK_TZ)
        
        # Обновляем таблицу на :05, :15, :25, :35, :45, :55
        if now.minute % 10 == 5 and last_table_update_minute != now.minute:
            sheets_manager.update_table()
            last_table_update_minute = now.minute
            print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} | Форматирование таблицы", flush=True)

        # Полный цикл каждые 10 минут (на :00, :10, :20, :30...)
        if now.minute % 10 == 0 and last_full_update_minute != now.minute:
            sheets_manager.update_table()
            print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} | Форматирование таблицы", flush=True)
            bats = sheets_manager.get_bats()
            ranks = sheets_manager.get_ranks()
            jedi_prefixes = sheets_manager.get_jedi_prefixes()

            parser.form_players_list()
            bats = Bats(parser.server1_players_list, parser.server2_players_list, bats, jedi_prefixes, ranks)
            bats.make_dict_of_bats()
            update_bats_data(bats.dict_of_bats_server1, server=1)
            update_bats_data(bats.dict_of_bats_server2, server=2)

            sheets_manager.update_data('327')
            last_full_update_minute = now.minute
            print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} | Данные обновлены, следующая проверка через 10 минут", flush=True)
        
        time.sleep(10)

main()