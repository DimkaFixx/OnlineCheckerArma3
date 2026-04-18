from parcedata import Parser, Bats
from sheets import GoogleTableManager

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
"""
print(sheets_manager.get_data_of_users())


parser.form_players_list()

bats.make_dict_of_bats()
print(bats.dict_of_bats_server1)
print(bats.dict_of_bats_server2)"""