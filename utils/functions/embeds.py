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
def create_captain_embed(captain_1, captain_2):
    captain_embed = Embed(title="Captains")
    captain_embed.add_field(name="Captain one", value=captain_1, inline=False)
    captain_embed.add_field(name="Captain two", value=captain_2, inline=False)
    return captain_embed
def create_connect_embed(server):
    connect_embed = Embed(title=server["location"].upper())
    address = f"connect {server['ip']:{server['ports']['game']}}"
    connect_embed.add_field(name=address, value="GL & HF")
    return connect_embed
