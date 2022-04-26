from nextcord.ui import View
from utils.classes.buttons import PlayerVotingButton, SettingsOvertime, SettingsTeamDamage, SettingsReady, TeamSelectionButton, TeamSelectionVote, TeamSelectionAccept, TeamSelectionShuffle, CaptainSelectButton
from utils.classes.dropdowns import LocationDropdown, MapDropdown
from utils.functions.serverconfigs import create_config_file, send_config_file
from utils.classes.dathost import Dathost
from random import shuffle
import requests
from botconfig import API_BASE_URL, API_PORT
from scrimconfig import map_pool

class ScrimLobby(View):
    def __init__(self, title, host):
        super().__init__(timeout=600)
        self.dathost = Dathost()
        self.servers = self.dathost.get_servers()
        self.locations_in_use = []
        check_for_locations = requests.get(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrims/")
        for location in check_for_locations.json():
            self.locations_in_use.append(location["Scrim"]["server_id"])
        self.available_locations = [
            (server['location'], server['id']) for server in self.servers if server['players_online'] == 0 and server['id'] not in self.locations_in_use]
        self.map_pool = map_pool
        self.title = title
        self.host = host
        self.current_turn = 0
        self.current_title = title
        self.team_1 = []
        self.team_2 = []
        self.captain_1 = None
        self.captain_2 = None
        self.team1_steamIDs = []
        self.team2_steamIDs = []
        self.current_lobby = []
        self.overtime = False
        self.team_damage = True
        self.current_map = []
        self.location = None
        self.server_id = None
        self.match_id = None
        self.launch_success = False
        self.launch_data = None
        self.match_details = None
        self.get_data()
        self.settings_selections_window()
    def post_server(self):
        data = {
            "active": True,
            "location": self.location,
            "id": self.match_id,
            "server_id": self.server_id,
            "players": self.current_lobby

        }
        requests.post(f"http://{API_BASE_URL}:{API_PORT}/servers/",json=data)
        self.timeout = 240
        return self.launch_data
    def settings_selections_window(self):
        self.add_item(SettingsOvertime("overtime", self.host))
        self.add_item(SettingsTeamDamage("team damage", self.host))
        self.add_item(SettingsReady("ready", self.host))
        self.add_item(MapDropdown(self.map_pool))
        self.add_item(LocationDropdown(self.available_locations))
    def teams_selection_window(self):
        self.clear_items()
        server_details = self.dathost.server_details(self.server_id)
        self.launch_data = server_details.json()
        self.add_item(TeamSelectionButton("Join team one", self.current_title, 1))
        self.add_item(TeamSelectionButton("Join team two", self.current_title, 2))
        self.add_item(TeamSelectionVote("vote for teams", self.host))
        self.add_item(TeamSelectionShuffle("Shuffle", self.current_title, self.host))
        self.add_item(TeamSelectionAccept("Launch", self.host))
    def captain_selection_window(self):
        self.clear_items()
        self.add_item(CaptainSelectButton("Captain ONE", 1))
        self.add_item(CaptainSelectButton("Captain TWO", 2))
    def teams_voting_window(self):
        self.clear_items()
        self.team_1.clear()
        self.team_1.append(self.captain_1)
        self.team_2.clear()
        self.team_2.append(self.captain_2)
        self.update_lobby()
        for player in self.current_lobby:
            if player is not self.captain_1 and player is not self.captain_2:
                self.add_item(PlayerVotingButton(
                        player, self.captain_1, self.captain_2))
    def gather_steam64(self):
        for user in self.match_details["players"]:
            if user["username"] in self.match_details["lobby"]["team_one"]:
                self.team1_steamIDs.append(str(user["steam64"]))
            elif user["username"] in self.match_details["lobby"]["team_two"]:
                self.team2_steamIDs.append(str(user["steam64"]))
    def initialize_server(self):
        server_data = self.launch_data
        ftp_password = server_data["ftp_password"]
        host = server_data["ip"]
        config_file = create_config_file(self.current_map, self.match_details["lobby"]["id"], self.team1_steamIDs, self.team2_steamIDs,
                                        captain1="ABIS",
                                            captain2="ABIS")
        send_config_file(config_file, host, self.server_id, ftp_password)
    def start_server(self):
        self.gather_steam64()
        self.initialize_server()
        self.dathost.start_server(self.server_id)
   

    def get_data(self):
        payload = {
            "title": self.current_title
        }
        
        check_for_lobby = requests.get(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=payload).json()
        try:
            self.team_1 = check_for_lobby["lobby"]["team_one"]
            self.team_2 = check_for_lobby["lobby"]["team_two"]
            self.current_lobby = [player["username"] for player in check_for_lobby["players"]]
            self.match_id = check_for_lobby["lobby"]["id"]
            self.match_details = check_for_lobby
            return self.team_1, self.team_2, self.current_lobby
        except:
            self.timeout = 1
            return self.team_1, self.team_2, self.current_lobby
    def add_team_one(self, user):
        self.team_1.append(user)
    def add_team_two(self, user):
        self.team_2.append(user)
    def get_teams(self):
        return self.team_1, self.team_2
    def check_teams(self):
        return len(self.team_1) == 5 and len(self.team_2) == 5
    def check_current_turn(self):
        return self.current_turn
    def change_turn(self):
        self.current_turn += 1
    def set_captain_one(self, user):
        self.captain_1 = user
    def set_captain_two(self, user):
        self.captain_2 = user
    def get_captains(self):
        return self.captain_1, self.captain_2
    def join_team_one(self, user):
        if user in self.current_lobby and len(self.team_1) <= 4:
            if user in self.team_2:
                self.team_2.remove(user)
            self.team_1.append(user)
    def join_team_two(self, user):
        if user in self.current_lobby and len(self.team_2) <= 4:
            if user in self.team_1:
                self.team_1.remove(user)
            self.team_2.append(user)
    def update_lobby(self):
        for user in self.team_1:
            if user not in self.current_lobby:
                self.team_1.remove(user)
        for user in self.team_2:
            if user not in self.current_lobby:
                self.team_2.remove(user)
        
        data = {
            "title": self.title,
            "user": None,
            "overtime": self.overtime,
            "team_damage": self.team_damage,
            "captain_one": self.captain_1,
            "captain_two": self.captain_2,
            "current_map": str(self.current_map),
            "server_id": self.server_id,
            "team_one": self.team_1,
            "team_two": self.team_2,
        }
        lobby = requests.put(f"http://{API_BASE_URL}:{API_PORT}/reenit/", json=data)
        if lobby.status_code == 404:
            self.stop()
    def shuffle(self):
        shuffle(self.current_lobby)
        self.team_1 = self.current_lobby[-5:]
        self.team_2 = self.current_lobby[:-5]
        self.update_lobby()
    def get_teams(self):
        return self.team_1, self.team_2
    def get_lobby(self):
        return self.current_lobby
    def set_overtime(self):
        self.overtime = not self.overtime
    def set_team_damage(self):
        self.team_damage = not self.team_damage
    def set_location_and_server_id(self, location):
        self.location = location
        index = [location[0] for location in self.available_locations].index(location)
        self.server_id = self.available_locations[index][1]
    def set_map(self, new_map):
        self.current_map.append(new_map)
    def get_settings(self):
        return self.overtime, self.team_damage, self.current_map, self.location
    async def on_error(self, error, item, interaction):
        print(f"{error}\n{item}\n{interaction}")
    async def on_timeout(self):
        self.clear_items()