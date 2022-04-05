from nextcord import Embed


def create_settings_embed(overtime_status=False, team_damage_status=True, current_map=None, location=None):
    settings_embed = Embed(title="Current settings")
    settings_embed.add_field(name="overtime", value=overtime_status)
    settings_embed.add_field(name="team damage", value=team_damage_status)
    settings_embed.add_field(name="current map", value=current_map)
    settings_embed.add_field(name="location", value=location)
    return settings_embed


def create_teams_embed(team_1=[], team_2=[], captain_1=None, captain_2=None):
    teams_embed = Embed(title="Teams")
    teams_embed.add_field(name="Captain 1", value=captain_1)
    teams_embed.add_field(name="Captain 2", value=captain_2)
    teams_embed.add_field(name="Team1", value=team_1, inline=False)
    teams_embed.add_field(name="Team2", value=team_2, inline=False)

    return teams_embed


def create_connect_embed(data):
    connect_embed = Embed(title=data[0])
    connect_embed.add_field(name=data[1], value="GL & HF")
    return connect_embed
