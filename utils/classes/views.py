from nextcord.ui import View
from nextcord.ui import Button
from nextcord import ButtonStyle, Interaction
from utils.classes.buttons import PlayerVotingButton, SettingsOvertime, SettingsTeamDamage, SettingsReady, TeamSelectionButton, TeamSelectionVote, TeamSelectionAccept, TeamSelectionShuffle, LaunchButton
from utils.classes.dropdowns import LocationDropdown, MapDropdown
from utils.functions.serverconfigs import create_config_file, send_config_file, delete_config_file
from utils.classes.dathost import Dathost
from utils.classes.database import Database
from random import shuffle, sample, randint
import requests
from botconfig import API_BASE_URL, API_PORT


class TeamsVote(View):
    def __init__(self, player_list, captain1, captain2, title):
        super().__init__(timeout=None)
        self.player_list = player_list
        self.title = title
        self.team1 = []
        self.team2 = []
        self.current_turn = 0
        self.captain1 = captain1
        self.captain2 = captain2
        self.team1.append(captain1)
        self.team2.append(captain2)
        self.player_list.remove(captain1)
        self.player_list.remove(captain2)
        for player in self.player_list:
            self.add_item(PlayerVotingButton(
                    player, self.captain1, self.captain2))

    def add_team_one(self, user):
        self.team1.append(user)

    def add_team_two(self, user):
        self.team2.append(user)

    def get_teams(self):
        return self.team1, self.team2

    def check_teams(self):
        return len(self.team1) == 5 and len(self.team2) == 5

    def check_current_turn(self):
        return self.current_turn

    def change_turn(self):
        self.current_turn += 1

    def finalize(self):
        team1, team2 = self.get_teams()
        data = {
            "title": self.title,
            "team_one": team1,
            "team_two": team2
        }
        requests.put(f"http://{API_BASE_URL}:{API_PORT}/reenit/", json=data)
        self.stop()


class TeamSelection(View):
    def __init__(self, title):
        super().__init__(timeout=None)
        self.current_title = title
        self.team_1 = []
        self.team_2 = []
        self.current_lobby = []
        self.voting = False
        self.add_item(TeamSelectionButton("Join team one", self.current_title, 1))
        self.add_item(TeamSelectionButton("Join team two", self.current_title, 2))
        self.add_item(TeamSelectionVote("vote for teams"))
        self.add_item(TeamSelectionShuffle("Shuffle", self.current_title))
        self.add_item(TeamSelectionAccept("Accept current teams"))
        self.get_data()
    def get_data(self):
        payload = {
            "title": self.current_title
        }
        check_for_lobby = requests.get(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=payload)
        print(check_for_lobby.json())
        self.team_1 = check_for_lobby.json()["lobby"][0]["team_one"]
        self.team_2 = check_for_lobby.json()["lobby"][0]["team_two"]
        self.current_lobby = [player["username"] for player in check_for_lobby.json()["players"]]
        return check_for_lobby.json()
    def set_captains(self):
        self.captain1, self.captain2 = sample(self.current_lobby, 2)
        self.team_1 = [self.captain1]
        self.team_2 = [self.captain2]
        return self.captain1, self.captain2

    def join_team_one(self, user):
        print(self.team_1)
        if user in self.current_lobby and len(self.team_1) <= 4:
            if user in self.team_2:
                self.team_2.remove(user)
            self.team_1.append(user)

    def join_team_two(self, user):
        if user in self.current_lobby and len(self.team_2) <= 4:
            if user in self.team_1:
                self.team_1.remove(user)
            self.team_2.append(user)

    def shuffle(self):
        shuffle(self.current_lobby)
        self.team_1 = self.current_lobby[-5:]
        self.team_2 = self.current_lobby[:-5]

    def set_voting(self):
        self.voting = not self.voting

    def get_teams(self):
        return self.team_1, self.team_2

    def set_ready(self):
        self.stop()

    def initiate_voting(self):
        return self.voting


class Settings(View):
    def __init__(self, available_locations, map_pool):
        super().__init__(timeout=None)
        self.overtime = False
        self.team_damage = True
        self.map = []
        self.location = None
        self.available_locations = available_locations
        self.add_item(SettingsOvertime("overtime"))
        self.add_item(SettingsTeamDamage("team damage"))
        self.add_item(SettingsReady("ready"))
        self.add_item(MapDropdown(map_pool))
        self.add_item(LocationDropdown(self.available_locations))

    def set_overtime(self):
        self.overtime = not self.overtime

    def set_team_damage(self):
        self.team_damage = not self.team_damage

    def set_location(self, location):
        self.location = location

    def set_map(self, new_map):
        self.map.append(new_map)

    def get_settings(self):
        return self.overtime, self.team_damage, self.map, self.location

    def set_ready(self):
        self.stop()


class Launch(View):
    def __init__(self, team1, team2, map, location):
        super().__init__(timeout=None)
        self.location = location
        self.team1 = team1
        self.team2 = team2
        self.map = map
        self.add_item(LaunchButton("Restart", self.location))

    async def launch_server(self):
        dathost = Dathost()
        server_launch = dathost.start_server(self.location)
        if server_launch.status_code == 200:
            return await dathost.server_details(self.location)
        return False

    def launch_success(self):
        pass
        # self.stop()
