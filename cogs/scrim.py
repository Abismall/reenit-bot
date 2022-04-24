import nextcord
from nextcord.ext import commands
from utils.classes.views import Launch, Settings, TeamSelection, TeamsVote
from utils.steam.steamidParser import steam64_from_url
from utils.classes.database import Database
from utils.classes.dathost import Dathost
from utils.functions.embeds import create_settings_embed, create_teams_embed, create_connect_embed
from utils.functions.serverconfigs import send_config_file, create_config_file, delete_config_file
from botconfig import TESTING_GUILD_IDS, API_BASE_URL, API_PORT
from scrimconfig import map_pool
import requests


class scrim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lobby = []
        self.map_pool = map_pool
        self.dathost = Dathost()
        self.database = Database()
    @nextcord.slash_command(name="start_scrim", description="join scrim waiting lobby", guild_ids=[TESTING_GUILD_IDS])
    async def start_scrim(self, ctx, title: str, password: str):
        login = {
            "username": ctx.user.name,
            "password": password
        }
        login = requests.post(f"http://{API_BASE_URL}:{API_PORT}/login", data=login)
        if login.status_code == 403:
            await ctx.send("login failure")
        if login.status_code == 200:
            auth = {
                "Authorization": login.json()["token_type"] + " " + login.json()["token"]
            }
            data = {
                "title": title
            }
            new_scrim = requests.post(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrims/", headers=auth, json=data)
            await ctx.send(new_scrim.json())
    @nextcord.slash_command(name="join_scrim", description="join scrim waiting lobby", guild_ids=[TESTING_GUILD_IDS])
    async def join_scrim1(self, ctx, title: str, password: str):
        data = {
            "title": title
        }
        check_for_lobby = requests.get(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=data)
        if check_for_lobby.status_code == 200:
            data = {
                "username": ctx.user.name,
                "password": password
            }
            login = requests.post(f"http://{API_BASE_URL}:{API_PORT}/login", data=data)
            if login.status_code == 200:
                auth = {
                    "Authorization": login.json()["token_type"] + " " + login.json()["token"]
                }
                join_lobby = requests.post(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/{title}", headers=auth)
                if join_lobby.status_code == 200:
                    await ctx.send(join_lobby.json())
                elif join_lobby.status_code == 404:
                    await ctx.send("no such lobby")
                elif join_lobby.status_code == 409:
                    await ctx.send(join_lobby.json())
            else:
                await ctx.send("login failure")
        elif check_for_lobby.status_code == 404:
            await ctx.send("no such lobby")
    @nextcord.slash_command(name="leave_scrim", description="leave", guild_ids=[TESTING_GUILD_IDS])
    async def leave_scrim(self, ctx, password: str):
        data = {
            "username": ctx.user.name,
            "password": password
        }
        login = requests.post(f"http://{API_BASE_URL}:{API_PORT}/login", data=data)
        if login.status_code == 200:
            auth = {
                "Authorization": login.json()["token_type"] + " " + login.json()["token"]
            }
            leave_lobby = requests.delete("http://{API_BASE_URL}:{API_PORT}/reenit/", headers=auth)
            if leave_lobby.status_code == 200:
                await ctx.send(f"{ctx.user.name} left")
            elif leave_lobby.status_code == 409:
                await ctx.send("currently not in a lobby")
            else:
                await ctx.send("error leaving scrim system")
        else:
            await ctx.send("login failure")
    @nextcord.slash_command(name="host_scrim", description="join scrim waiting lobby", guild_ids=[TESTING_GUILD_IDS])
    async def host_scrim(self, ctx, title: str):
        data = {
            "title": title
        }
        check_for_lobby = requests.get(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=data)
        if check_for_lobby.status_code == 404:
            await ctx.send("no such lobby")
        if check_for_lobby.status_code == 200:
            lobby_title = check_for_lobby.json()["lobby"][0]["title"]
            lobby_players = [player["username"] for player in check_for_lobby.json()["players"]]
            if len(check_for_lobby.json()["players"]) >= 0:
                await ctx.send(f"Starting {lobby_title}", delete_after=5)
                servers = self.dathost.get_servers()
                server_locations = [
                    (server['location'], server['id']) for server in servers if server['players_online'] == 0]
        
                settings = Settings([location[0]
                                    for location in server_locations], self.map_pool)
                embed = create_settings_embed()
                menu = await ctx.send("Menu", view=settings, embed=embed)
                await settings.wait()
                team_selection = TeamSelection(lobby_title)
                embed = create_teams_embed()
                await menu.edit(view=team_selection, embed=embed)
                await team_selection.wait()
                if team_selection.initiate_voting() == True:
                    captain1, captain2 = team_selection.set_captains()
                    captains_vote_teams = TeamsVote(lobby_players, captain1, captain2, lobby_title)
                    team_embed = create_teams_embed(
                        [captain1], [captain2], captain1, captain2)
                    await menu.edit(view=captains_vote_teams, embed=team_embed)
                    await captains_vote_teams.wait()
                overtime, team_damage, map, location = settings.get_settings()
                index = [x[0] for x in server_locations].index(location)
                server_id = server_locations[index][1]
                server_data = await self.dathost.server_details(server_id)
                ftp_password = server_data.json()["ftp_password"]
                host = server_data.json()["ip"]
                match_details = team_selection.get_data()
                team1_steamIDs = []
                team2_steamIDs = []
                for user in match_details["players"]:
                    if user["username"] in match_details["lobby"][0]["team_one"]:
                        team1_steamIDs.append(str(user["steam64"]))
                    elif user["username"] in match_details["lobby"][0]["team_two"]:
                        team2_steamIDs.append(str(user["steam64"]))
                config_file = create_config_file(map, match_details["lobby"][0]["id"], team1_steamIDs, team2_steamIDs,
                                                captain1="ABIS",
                                                 captain2="ABIS")
                status = await send_config_file(config_file, host, server_id, ftp_password)
                launch = Launch(match_details["lobby"][0]["team_one"], match_details["lobby"][0]["team_two"], map, server_id)
                await menu.edit(view=launch)
                server_launch = await launch.launch_server()
                data = {
                    "active": True,
                    "location": server_locations[index][0],
                    "id": match_details["lobby"][0]["id"],
                    "server_id": server_id,
                    "players": lobby_players

                }
                current_game = requests.post(f"http://{API_BASE_URL}:{API_PORT}/servers/",json=data)
                launch_json = server_launch.json()
                content = f" {launch_json['location']}", f"connect {launch_json['ip']}:{launch_json['ports']['game']}"
                connect_embed = create_connect_embed(content)
                await menu.edit(content=content, embed=connect_embed)
            else:
                await ctx.send("Not enough players")
    @nextcord.slash_command(name="register_account", description="register", guild_ids=[TESTING_GUILD_IDS])
    async def register_user(self, ctx, password: str, steam64: str):
        user = {"username": ctx.user.name, "password":password,"steam64":int(steam64)}
        user_registration = requests.post(f"http://{API_BASE_URL}:{API_PORT}/users/", json=user)
        if user_registration.status_code == 201:
            await ctx.send(f"{ctx.user.name} has been registered")

def setup(bot):
    bot.add_cog(scrim(bot))
