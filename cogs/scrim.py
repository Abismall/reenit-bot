import nextcord
from nextcord.ext import commands
from utils.classes.views import Launch, Settings, TeamSelection, TeamsVote
from utils.steam.steamidParser import steam64_from_url
from utils.classes.database import Database
from utils.classes.dathost import Dathost
from utils.functions.embeds import create_settings_embed, create_teams_embed, create_connect_embed
from botconfig import TESTING_GUILD_IDS
from scrimconfig import server_locations


class scrim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lobby = []

    @nextcord.slash_command(name="join_lobby1", description="join scrim waiting lobby", guild_ids=[TESTING_GUILD_IDS])
    async def join_scrim(self, ctx):
        if ctx.user.name not in self.lobby:
            database = Database()
            user = database.fetch_user(ctx.user.name)
            if user:
                self.lobby.append(ctx.user.name)
                await ctx.send(f"{user[1]} Joined lobby", delete_after=5)
            if not user:
                await ctx.send("You are not registered", delete_after=5)
        elif ctx.user.name in self.lobby:
            await ctx.send("Already in the lobby", delete_after=5)
        if len(self.lobby) >= 1:
            settings = Settings(server_locations)
            # await settings.get_available_regions()
            embed = create_settings_embed()
            menu = await ctx.send("Menu", view=settings, embed=embed)
            settings_status = await settings.wait()
            if settings_status == False:
                team_selection = TeamSelection(self.lobby)
                embed = create_teams_embed()
                await menu.edit(view=team_selection, embed=embed)
            else:
                pass
            await team_selection.wait()
            if team_selection.initiate_voting() == True:
                captain1, captain2 = team_selection.set_captains()
                captains_vote_teams = TeamsVote(self.lobby, captain1, captain2)
                team_embed = create_teams_embed(
                    [captain1], [captain2], captain1, captain2)
                await menu.edit(view=captains_vote_teams, embed=team_embed)
                await captains_vote_teams.wait()
            else:
                overtime, team_damage, map, location = settings.get_settings()
                team1, team2 = team_selection.get_teams()
                host = "1"
                ftp_user = "2"
                ftp_password = "3"
                locations_list = settings.show_available_locations()
                index = [x[0] for x in locations_list].index(location)
                server_id = locations_list[index][1]
                launch = Launch(team1, team2, map,  host,
                                ftp_user, ftp_password, server_id)
                await menu.edit(view=launch)
                server_launch = await launch.launch_server()
                launch_json = server_launch.json()
                content = f" {launch_json['location']}", f"connect {launch_json['ip']}:{launch_json['ports']['game']}"
                connect_embed = create_connect_embed(content)
                await menu.edit(content=content, embed=connect_embed)


def setup(bot):
    bot.add_cog(scrim(bot))
