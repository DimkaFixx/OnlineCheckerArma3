import requests
from dotenv import load_dotenv
import os
import re
import time

load_dotenv()
class Servers:
    def __init__(self):
        self.s1_id = os.getenv("S1_ID")
        self.s2_id = os.getenv("S2_ID")
    
    def get_s1(self):
        try:
            response = requests.get(f"https://api.battlemetrics.com/servers/{self.s1_id}?include=player")
            return response.json()
        except:
            time.sleep(10)
            return self.get_s1()
    
    def get_s2(self):
        try:
            response = requests.get(f"https://api.battlemetrics.com/servers/{self.s2_id}?include=player")
            return response.json()
        except:
            time.sleep(10)
            return self.get_s2()

class Parser:
    def __init__(self):
        self.servers = Servers()
        self.server1_players_list = []
        self.server2_players_list = []
    
    def form_players_list(self):
        s1_data = self.servers.get_s1()
        s2_data = self.servers.get_s2()
        server1_players_list = []
        server2_players_list = []
        for player in s1_data["included"]:
            if player["type"] == "player":
                server1_players_list.append(player["attributes"]["name"])
        for player in s2_data["included"]:
            if player["type"] == "player":
                server2_players_list.append(player["attributes"]["name"])
        self.server1_players_list = server1_players_list
        self.server2_players_list = server2_players_list
        return server1_players_list, server2_players_list

class Bats:
    def __init__(self, s1_list, s2_list, bats, jedi_prefixes, ranks):
        self.s1_list = s1_list
        self.s2_list = s2_list
        self.bats = bats
        self.jedi_prefixes = jedi_prefixes
        self.ranks = ranks
        self.dict_of_bats_server1 = {}
        self.dict_of_bats_server2 = {}
        for bat in bats:
            self.dict_of_bats_server1[bat] = []
            self.dict_of_bats_server2[bat] = []
        self.dict_of_bats_server1["other"] = []
        self.dict_of_bats_server2["other"] = []
    
    def make_dict_of_bats(self):
        for player in self.s1_list:
            self.format_player_bat(player, 1)
        for player in self.s2_list:
            self.format_player_bat(player, 2)

    def format_player_bat(self, player_nickname, server_num):
        player_nickname = str(player_nickname)

        if not "[" in player_nickname:
            if server_num == 1:
                self.dict_of_bats_server1["other"].append(player_nickname)
            elif server_num == 2:
                self.dict_of_bats_server2["other"].append(player_nickname)
            return player_nickname
        
        #Определение джедаев (подразделений джедаев)
        bat_or_spec = player_nickname.split("|")[-1].replace(" ", "") if "|" in player_nickname else ""
        player_nickname = player_nickname.split("|")[0].strip() if "|" in player_nickname else player_nickname
        if bat_or_spec in self.bats:
            player_nickname = re.sub(r'\s*\[.*?\]\s*', '', player_nickname)
            player_nickname = self.format_player_nickname_not_with_bat(player_nickname)

            if server_num == 1:
                self.dict_of_bats_server1[bat_or_spec].append(player_nickname)
            elif server_num == 2:
                self.dict_of_bats_server2[bat_or_spec].append(player_nickname)

            return player_nickname, bat_or_spec
        

        #определение подразделения

        #определение RC (у них нет цифр, они по отрядам)
        bat = player_nickname.replace("[", "").split("]")[0]
        if 'RC' in bat and not any(bats in bat for bats in self.bats if bats != "RC"):
            player_nickname = re.sub(r'\s*\[.*?\]\s*', '', player_nickname)
            player_nickname = self.format_player_nickname_not_with_bat(player_nickname)

            if server_num == 1:
                self.dict_of_bats_server1["RC"].append(player_nickname)
            elif server_num == 2:
                self.dict_of_bats_server2["RC"].append(player_nickname)
            
            return player_nickname, "RC"
        
        #Конкорд
        if "C-3" in bat:
            player_nickname = re.sub(r'\s*\[.*?\]\s*', '', player_nickname)
            player_nickname = self.format_player_nickname_not_with_bat(player_nickname)

            if server_num == 1:
                self.dict_of_bats_server1["C-3"].append(player_nickname)
            elif server_num == 2:
                self.dict_of_bats_server2["C-3"].append(player_nickname)
            
            return player_nickname, "C-3"

        #Все, кроме джидов
        bat = bat.split("-")[1].strip() if "-" in bat else bat.strip()
        if bat in self.bats:
            player_nickname = re.sub(r'\s*\[.*?\]\s*', '', player_nickname)
            player_nickname = self.format_player_nickname_not_with_bat(player_nickname)

            if server_num == 1:
                self.dict_of_bats_server1[bat].append(player_nickname)
            elif server_num == 2:
                self.dict_of_bats_server2[bat].append(player_nickname)

            return player_nickname, bat
        
        #Тут мы понимаем, что джедаи невалидированы
        if bat in self.jedi_prefixes:
            player_nickname = re.sub(r'\s*\[.*?\]\s*', '', player_nickname)
            player_nickname = self.format_player_nickname_not_with_bat(player_nickname)

            if server_num == 1:
                self.dict_of_bats_server1["Jedi"].append(player_nickname)
            elif server_num == 2:
                self.dict_of_bats_server2["Jedi"].append(player_nickname)
                
            return player_nickname, "Jedi"
        
        
        if server_num == 1:
            self.dict_of_bats_server1["other"].append(player_nickname)
        elif server_num == 2:
            self.dict_of_bats_server2["other"].append(player_nickname)
        
        return player_nickname

    #Сюда идет звание + позвыной (мб + номер или + ФИ)
    def format_player_nickname_not_with_bat(self, player_nickname):
        if any(rank in player_nickname for rank in self.ranks):
            for rank in self.ranks:
                if rank+" " in player_nickname:
                    player_nickname = player_nickname.replace(rank+" ", "")
                    break
        else:
            player_nickname = player_nickname.strip()
        
        #На этом этапе у нас или ник или номер, или номер + ник или ФИ джедая, 
        
        player_nick_or_num = player_nickname.split(" ")
        if len(player_nick_or_num) == 1:
            return player_nick_or_num[0]
        if player_nick_or_num[0].isdigit():
            return player_nick_or_num[1]
        return player_nickname


