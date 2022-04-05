from nextcord.ui import View
from nextcord.ui import Button
from nextcord import ButtonStyle, Interaction
from utils.classes.buttons import PlayerButton, SettingsOvertime, SettingsTeamDamage, SettingsReady, TeamSelectionButton1, TeamSelectionButton2, TeamSelectionVote, TeamSelectionAccept, TeamSelectionShuffle, LaunchButton
from utils.classes.dropdowns import LocationDropdown, MapDropdown
from utils.functions.serverconfigs import create_config_file, send_config_file, delete_config_file
from utils.classes.dathost import Dathost
from utils.classes.database import Database
from random import shuffle, sample, randint


class TeamsVote(View):
    def __init__(self, player_list, captain1, captain2):
        super().__init__(timeout=None)
        self.player_list = player_list
        self.team1 = []
        self.team2 = []
        self.current_turn = 0
        self.captain1 = captain1
        self.captain2 = captain2
        self.team1.append(captain1)
        self.team2.append(captain2)
        for player in player_list:
            if player is not self.captain1 and player is not self.captain2:
                self.add_item(PlayerButton(
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
        self.stop()


class TeamSelection(View):
    def __init__(self, current_lobby):
        super().__init__(timeout=None)
        self.current_lobby = current_lobby
        self.team_1 = []
        self.team_2 = []
        self.voting = False
        self.add_item(TeamSelectionButton1("Join team one"))
        self.add_item(TeamSelectionButton2("Join team two"))
        self.add_item(TeamSelectionVote("vote for teams"))
        self.add_item(TeamSelectionShuffle("Shuffle"))
        self.add_item(TeamSelectionAccept("Accept current teams"))

    def set_captains(self):
        self.captain1, self.captain2 = sample(self.current_lobby, 2)
        self.team_1 = [self.captain1]
        self.team_2 = [self.captain2]
        return self.captain1, self.captain2

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
        self.map = None
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
        self.map = new_map

    def get_settings(self):
        return self.overtime, self.team_damage, self.map, self.location

    def set_ready(self):
        self.stop()

    # async def set_available_regions(self):
    #     available_location = []
    #     dathost = Dathost()
    #     for location in server_locations:
    #         current_location = server_locations[location]
    #         for server in current_location:
    #             current_server = await dathost.server_details(server)
    #             if current_server is not None and current_server.status_code == 200:
    #                 data = current_server.json()
    #                 if data['players_online'] == 0:
    #                     available_location.append((location, server))
    #     self.available_locations = available_location
    #     self.add_item(LocationDropdown(self.available_locations))
    #     return self.available_locations

    def show_available_locations(self):
        return self.available_locations


class Launch(View):
    def __init__(self, team1, team2, map,  host, ftp_user, ftp_password, location):
        super().__init__(timeout=None)
        self.host = host
        self.location = location
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
        self.team1 = team1
        self.team2 = team2
        self.team1_id = []
        self.team2_id = []
        self.match_id = randint(0, 100000000000000)
        self.map = map
        self.config_file = None
        self.add_item(LaunchButton("Restart", self.location))
        self.get_steam64()

    def get_steam64(self):
        database = Database()
        for user in self.team1:
            user_id = database.fetch_user(user)
            self.team1_id.append(user_id)
        for user in self.team2:
            user_id = database.fetch_user(user)
            self.team2_id.append(user_id)

    def create_config_bytes(self):
        self.config_file = create_config_file(
            self.map, self.match_id, self.team1_id, self.team2_id)

    def send_config_file(self):
        status = send_config_file(
            self.config_file, self.host, self.ftp_user, self.ftp_password)
        return status

    def delete_config_file(self):
        status = delete_config_file(self.ftp_user, self.ftp_password)
        return status

    async def launch_server(self):
        dathost = Dathost()
        server_launch = dathost.start_server(self.location)
        if server_launch.status_code == 200:
            return await dathost.server_details(self.location)
        return False

    def launch_success(self):
        pass
        # self.stop()
