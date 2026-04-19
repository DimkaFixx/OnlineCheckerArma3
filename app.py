from parcedata import Parser, Bats
from sheets import GoogleTableManager
from db import update_bats_data, get_players_data
import time

def main():
    sheets_manager = GoogleTableManager()
    sheets_manager.connect()
    parser = Parser()

    while True:
        sheets_manager.update_table()

        bats = sheets_manager.get_bats()
        ranks = sheets_manager.get_ranks()
        jedi_prefixes = sheets_manager.get_jedi_prefixes()

        parser.form_players_list()
        bats = Bats(parser.server1_players_list, parser.server2_players_list, bats, jedi_prefixes, ranks)
        bats.make_dict_of_bats()
        update_bats_data(bats.dict_of_bats_server1, server=1)
        update_bats_data(bats.dict_of_bats_server2, server=2)

        sheets_manager.update_data('796')
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | Данные обновлены, следующая проверка через 10 минут", flush=True)
        time.sleep(10*60)

main()