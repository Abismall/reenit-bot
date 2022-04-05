from nextcord import ButtonStyle, Interaction
from nextcord.ui import Button
from utils.functions.embeds import create_settings_embed, create_teams_embed
from utils.classes.dathost import Dathost


class LaunchButton(Button):
    def __init__(self, label, server_id):
        super().__init__(style=ButtonStyle.green, label=label, disabled=True)
        self.server_id = server_id
        self.dathost = Dathost()

    async def callback(self, interaction: Interaction):
        pass


class PlayerButton(Button):
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


class TeamSelectionButton1(Button):
    def __init__(self, label):
        super().__init__(style=ButtonStyle.red, label=label)

    async def callback(self, interaction=Interaction):
        user = interaction.user.name
        self.view.join_team_one(user)
        team1, team2 = self.view.get_teams()
        if len(team1) == 5:
            self.disabled = True
        else:
            self.disabled = False
        teams_embed = create_teams_embed(team1, team2)
        await interaction.response.edit_message(view=self.view, embed=teams_embed)


class TeamSelectionButton2(Button):
    def __init__(self, label):
        super().__init__(style=ButtonStyle.blurple, label=label)

    async def callback(self, interaction=Interaction):
        user = interaction.user.name
        self.view.join_team_two(user)
        team1, team2 = self.view.get_teams()
        if len(team2) == 5:
            self.disabled = True
        else:
            self.disabled = False
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
    def __init__(self, label):
        super().__init__(style=ButtonStyle.green, label=label, row=1)

    async def callback(self, interaction=Interaction):
        self.view.shuffle()
        team1, team2 = self.view.get_teams()
        teams_embed = create_teams_embed(team1, team2)
        await interaction.response.edit_message(view=self.view, embed=teams_embed)
