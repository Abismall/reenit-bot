from nextcord import ButtonStyle, Interaction
from nextcord.ui import Button
from utils.functions.embeds import create_settings_embed, create_teams_embed
from utils.classes.dathost import Dathost
from botconfig import API_BASE_URL, API_PORT
import requests


class LaunchButton(Button):
    def __init__(self, label, server_id):
        super().__init__(style=ButtonStyle.green, label=label, disabled=True)
        self.server_id = server_id
        self.dathost = Dathost()

    async def callback(self, interaction: Interaction):
        pass


class PlayerVotingButton(Button):
    def __init__(self, player, captain1, captain2):
        super().__init__(style=ButtonStyle.green, label=player)
        self.captain1 = captain1
        self.captain2 = captain2

    async def callback(self, interaction: Interaction):
        view = self.view
        user = interaction.user.name
        current_turn = view.check_current_turn()
        player = self.label
        if user == self.captain1 and current_turn == 0:
            view.add_team_one(player)
            view.change_turn()
            self.disabled = True
        elif user == self.captain2 and current_turn == 1:
            view.add_team_two(player)
            view.change_turn()
            self.disabled = True
        elif user == self.captain2 and current_turn == 2:
            view.add_team_two(player)
            view.change_turn()
            self.disabled = True
        elif user == self.captain1 and current_turn == 3:
            view.add_team_one(player)
            view.change_turn()
            self.disabled = True
        elif user == self.captain1 and current_turn == 4:
            view.add_team_one(player)
            view.change_turn()
            self.disabled = True
        elif user == self.captain2 and current_turn == 5:
            view.add_team_two(player)
            view.change_turn()
            self.disabled = True
        elif user == self.captain2 and current_turn == 6:
            view.add_team_two(player)
            view.change_turn()
            self.disabled = True
        elif user == self.captain1 and current_turn == 7:
            view.add_team_one(player)
            self.disabled = True
            view.finalize()
        team1, team2 = view.get_teams()
        self.style = ButtonStyle.danger
        team_embed = create_teams_embed(
            team1, team2, self.captain1, self.captain2)
        await interaction.response.edit_message(view=view, embed=team_embed)


class SettingsReady(Button):
    def __init__(self, label):
        super().__init__(style=ButtonStyle.green, label=label)

    async def callback(self, interaction=Interaction):
        self.view.set_ready()


class SettingsOvertime(Button):
    def __init__(self, label):
        super().__init__(style=ButtonStyle.gray, label=label)

    async def callback(self, interaction=Interaction):
        self.view.set_overtime()
        overtime, team_damage, map, location = self.view.get_settings()
        settings_embed = create_settings_embed(
            overtime, team_damage, map, location)
        await interaction.response.edit_message(view=self.view, embed=settings_embed)


class SettingsTeamDamage(Button):
    def __init__(self, label):
        super().__init__(style=ButtonStyle.gray, label=label)

    async def callback(self, interaction=Interaction):
        self.view.set_team_damage()
        overtime, team_damage, map, location = self.view.get_settings()
        settings_embed = create_settings_embed(
            overtime, team_damage, map, location)
        await interaction.response.edit_message(view=self.view, embed=settings_embed)


class TeamSelectionButton(Button):
    def __init__(self, label, title, team):
        super().__init__(style=ButtonStyle.blurple, label=label)
        self.title = title
        self.team = team
    async def callback(self, interaction=Interaction):
        team1,team2 = self.view.get_teams()
        if self.team == 1 and interaction.user.name not in team1:
            self.view.join_team_one(interaction.user.name)
        if self.team == 2 and interaction.user.name not in team2:
            self.view.join_team_two(interaction.user.name)
        team1, team2 = self.view.get_teams()
        data = {
            "title": self.title,
            "team_one": team1,
            "team_two": team2
        }
        print(team1, team2)
        x = requests.put(f"http://{API_BASE_URL}:{API_PORT}/reenit/", json=data)
        print(x)
        teams_embed = create_teams_embed(team1, team2)
        await interaction.response.edit_message(view=self.view, embed=teams_embed)


class TeamSelectionVote(Button):
    def __init__(self, label):
        super().__init__(style=ButtonStyle.green, label=label, row=1)

    async def callback(self, interaction=Interaction):
        self.view.set_voting()
        self.view.set_ready()


class TeamSelectionAccept(Button):
    def __init__(self, label):
        super().__init__(style=ButtonStyle.green, label=label)

    async def callback(self, interaction=Interaction):
        self.view.set_ready()


class TeamSelectionShuffle(Button):
    def __init__(self, label, title):
        super().__init__(style=ButtonStyle.green, label=label, row=1)
        self.title = title

    async def callback(self, interaction=Interaction):
        self.view.shuffle()
        team1, team2 = self.view.get_teams()
        data = {
            "title": self.title,
            "team_one": team1,
            "team_two": team2,
          
        }
        requests.put(f"http://{API_BASE_URL}:{API_PORT}/reenit/", json=data)
        teams_embed = create_teams_embed(team1, team2)
        await interaction.response.edit_message(view=self.view, embed=teams_embed)
