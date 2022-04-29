from nextcord import ButtonStyle, Interaction
from nextcord.ui import Button
from utils.functions.embeds import create_settings_embed, create_teams_embed, create_captain_embed, create_connect_embed
# class LaunchButton(Button):
#     def __init__(self, label):
#         super().__init__(style=ButtonStyle.danger, label=label)

#     async def callback(self, interaction: Interaction):
#         self.view.start_server()
#         await interaction.response.edit_message(view=self.view)


class PlayerVotingButton(Button):
    def __init__(self, player, captain_1, captain_2):
        super().__init__(style=ButtonStyle.green, label=player)
        self.captain1 = captain_1
        self.captain2 = captain_2
        self.finished = False

    async def callback(self, interaction: Interaction):
        current_turn = view.check_current_turn()
        view = self.view
        user = interaction.user.name
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
            self.view.update_lobby()
            self.finished = True
        if self.disabled == True:
            self.style = ButtonStyle.danger
        team1, team2 = view.get_teams()
        team_embed = create_teams_embed(
            team1, team2, self.captain1, self.captain2)
        await interaction.response.edit_message(view=view, embed=team_embed)
        if self.finished == True:
            server = self.view.get_launch_data()
            self.view.launch_window()
            launch_embed = create_connect_embed(server)
            await interaction.response.edit_message(view=self.view, embed=launch_embed)


class SettingsReady(Button):
    def __init__(self, label, host):
        super().__init__(style=ButtonStyle.green, label=label)
        self.host = host

    async def callback(self, interaction=Interaction):
        try:
            overtime, team_damage, current_map, location = self.view.get_settings()
            if interaction.user.name == self.host and len(current_map) > 0 and location != None:
                self.view.teams_selection_window()
                await interaction.response.edit_message(view=self.view)
        except:
            pass


class SettingsOvertime(Button):
    def __init__(self, label, host):
        super().__init__(style=ButtonStyle.gray, label=label)
        self.host = host

    async def callback(self, interaction=Interaction):
        if interaction.user.name == self.host:
            self.view.set_overtime()
            overtime, team_damage, map, location = self.view.get_settings()
            settings_embed = create_settings_embed(
                overtime, team_damage, map, location)
            await interaction.response.edit_message(view=self.view, embed=settings_embed)


class SettingsTeamDamage(Button):
    def __init__(self, label, host):
        super().__init__(style=ButtonStyle.gray, label=label)

    async def callback(self, interaction=Interaction):
        self.view.set_team_damage()
        overtime, team_damage, map, location = self.view.get_settings()
        settings_embed = create_settings_embed(
            overtime, team_damage, map, location)
        await interaction.response.edit_message(view=self.view, embed=settings_embed)


class CaptainSelectButton(Button):
    def __init__(self, label, id):
        super().__init__(style=ButtonStyle.blurple, label=label)
        self.id = id

    async def callback(self, interaction=Interaction):
        user = interaction.user.name
        self.view.get_data()
        self.view.update_lobby()
        current_lobby = self.view.get_lobby()
        captain_1, captain_2 = self.view.get_captains()
        if self.id == 1 and user in current_lobby and user != captain_2:
            self.view.set_captain_one(interaction.user.name)
            self.disabled = True
        if self.id == 2 and user in current_lobby and user != captain_1:
            self.view.set_captain_two(interaction.user.name)
            self.disabled = True
        captain_1, captain_2 = self.view.get_captains()
        self.view.update_lobby()
        captain_embed = create_captain_embed(captain_1, captain_2)
        await interaction.response.edit_message(view=self.view, embed=captain_embed)
        if captain_1 is not None and captain_2 is not None:
            self.view.update_lobby()
            self.view.teams_voting_window()


class TeamSelectionButton(Button):
    def __init__(self, label, title, team):
        super().__init__(style=ButtonStyle.blurple, label=label)
        self.title = title
        self.team = team

    async def callback(self, interaction=Interaction):
        try:
            self.view.get_data()
            team1, team2 = self.view.get_teams()
            current_lobby = self.view.get_lobby()
            if self.team == 1 and interaction.user.name in current_lobby and interaction.user.name not in team1:
                self.view.join_team_one(interaction.user.name)
            if self.team == 2 and interaction.user.name in current_lobby and interaction.user.name not in team2:
                self.view.join_team_two(interaction.user.name)
            self.view.update_lobby()
            team1, team2 = self.view.get_teams()
            teams_embed = create_teams_embed(team1, team2)
            await interaction.response.edit_message(view=self.view, embed=teams_embed)
        except:
            pass


class TeamSelectionVote(Button):
    def __init__(self, label, host):
        super().__init__(style=ButtonStyle.green, label=label, row=1)
        self.host = host

    async def callback(self, interaction=Interaction):
        if interaction.user.name == self.host:
            self.view.captain_selection_window()
            await interaction.response.edit_message(view=self.view)


class TeamSelectionAccept(Button):
    def __init__(self, label, host):
        super().__init__(style=ButtonStyle.green, label=label)
        self.host = host

    async def callback(self, interaction=Interaction):
        if interaction.user.name == self.host:
            launch_embed = create_connect_embed(self.view.get_launch_data())
            await interaction.response.edit_message(view=self.view, embed=launch_embed)
            self.view.launch_window()


class TeamSelectionShuffle(Button):
    def __init__(self, label, title, host):
        super().__init__(style=ButtonStyle.green, label=label, row=1)
        self.title = title
        self.host = host

    async def callback(self, interaction=Interaction):
        if interaction.user.name == self.host:
            self.view.shuffle()
            team1, team2 = self.view.get_teams()
            teams_embed = create_teams_embed(team1, team2)
            await interaction.response.edit_message(view=self.view, embed=teams_embed)
