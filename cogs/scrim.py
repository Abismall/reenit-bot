import nextcord
from nextcord.ext import commands
from utils.classes.views import ScrimLobby
from utils.classes.database import Database
from utils.steam.steamidParser import SteamID, steam64_from_url
from botconfig import TESTING_GUILD_IDS, API_BASE_URL, API_PORT
import requests


class scrim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lobby = []
        self.database = Database()
    @nextcord.slash_command(name="start_scrim", description="join scrim waiting lobby", guild_ids=TESTING_GUILD_IDS)
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
            await ctx.send(new_scrim.json()["detail"])
    @nextcord.slash_command(name="join_scrim", description="join scrim waiting lobby", guild_ids=TESTING_GUILD_IDS)
    async def join_scrim(self, ctx, title: str, password: str):
        query_data = {
            "title": title
        }
        check_for_lobby = requests.get(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=query_data)
        if check_for_lobby.status_code == 200:
            login_data = {
                "username": ctx.user.name,
                "password": password
            }
            login = requests.post(f"http://{API_BASE_URL}:{API_PORT}/login", data=login_data)
            if login.status_code == 200:
                auth = {
                    "Authorization": login.json()["token_type"] + " " + login.json()["token"]
                }
                join_lobby = requests.post(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=query_data, headers=auth)
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
    @nextcord.slash_command(name="leave_scrim", description="leave", guild_ids=TESTING_GUILD_IDS)
    async def leave_scrim(self, ctx, password: str):
        login_data = {
            "username": ctx.user.name,
            "password": password
        }
        login = requests.post(f"http://{API_BASE_URL}:{API_PORT}/login", data=login_data)
        if login.status_code == 200:
            auth = {
                "Authorization": login.json()["token_type"] + " " + login.json()["token"]
            }
            leave_lobby = requests.delete(f"http://{API_BASE_URL}:{API_PORT}/reenit/", headers=auth)
            if leave_lobby.status_code == 200:
                await ctx.send(f"{ctx.user.name} left")
            elif leave_lobby.status_code == 409:
                await ctx.send("currently not in a lobby")
            else:
                await ctx.send("error leaving scrim system")
        else:
            await ctx.send("login failure")
    @nextcord.slash_command(name="host_scrims", description="join scrim waiting lobby", guild_ids=TESTING_GUILD_IDS)
    async def host_scrim(self, ctx, title: str):
        data = {
            "title": title
        }
        check_for_lobby = requests.get(f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=data)
        check_ownership = requests.get(f"http://{API_BASE_URL}:{API_PORT}/users/user", json={"username": ctx.user.name})
        owner_id = check_ownership.json()["id"]
        if check_for_lobby.status_code == 404:
            await ctx.send("no such lobby")
        if check_for_lobby.status_code == 200 and owner_id != check_for_lobby.json()["lobby"]["owner_id"]:
            await ctx.send("only the owner can host")
        if check_for_lobby.status_code == 200:  
            view=ScrimLobby(title, ctx.user.name)
            await ctx.send(f"hosting {title}", delete_after=5)
            message = await ctx.send(title, view=view, delete_after=600)
            status = await view.wait()
            if status == False:
                await ctx.send(f"Error hosting {title} if this error persists contact reenitscrim@gmail.com", delete_after=25)
            await message.edit(delete_after=5)             
    @nextcord.slash_command(name="register_account", description="register", guild_ids=TESTING_GUILD_IDS)
    async def register(self, ctx, password: str, steam64: str):
        validity_check = SteamID(steam64).is_valid()
        if validity_check == False:
            steam64 = steam64_from_url(steam64)
        if steam64 is not None or validity_check == True:
            user = {"username": ctx.user.name, "password":password,"steam64":int(steam64)}        
            user_registration = requests.post(f"http://{API_BASE_URL}:{API_PORT}/users/", json=user)
            if user_registration.status_code == 201:
                await ctx.send(f"{ctx.user.name} has been registered")
            if user_registration.status_code == 400:
                await ctx.send(f"{ctx.user.name} has already registered")
        else:
            await ctx.send("invalid steam64")

def setup(bot):
    bot.add_cog(scrim(bot))
