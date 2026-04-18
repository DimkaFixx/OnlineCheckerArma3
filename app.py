from parcedata import Parser, Bats
from sheets import GoogleTableManager
from db import update_players_data, get_players_data

sheets_manager = GoogleTableManager()
sheets_manager.connect()
sheets_manager.update_table()
bats = sheets_manager.get_bats()
ranks = sheets_manager.get_ranks()
jedi_prefixes = sheets_manager.get_jedi_prefixes()


parser = Parser()
parser.form_players_list()
bats = Bats(parser.server1_players_list, parser.server2_players_list, bats, jedi_prefixes, ranks)
bats.make_dict_of_bats()
print(bats.dict_of_bats_server1)
print(bats.dict_of_bats_server2)

update_players_data(bats.dict_of_bats_server1, server=1)
update_players_data(bats.dict_of_bats_server2, server=2)

s1_data = get_players_data(parser.server1_players_list, server=1)
s2_data = get_players_data(parser.server2_players_list, server=2)

