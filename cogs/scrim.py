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
        login = requests.post(
            f"http://{API_BASE_URL}:{API_PORT}/login", data=login)
        if login.status_code == 403:
            await ctx.send("login failure", delete_after=15)
        if login.status_code == 200:
            auth = {
                "Authorization": login.json()["token_type"] + " " + login.json()["token"]
            }
            data = {
                "title": title
            }
            new_scrim = requests.post(
                f"http://{API_BASE_URL}:{API_PORT}/reenit/scrims/", headers=auth, json=data)
            await ctx.send(new_scrim.json()["detail"])

    @nextcord.slash_command(name="join_scrim", description="join scrim waiting lobby", guild_ids=TESTING_GUILD_IDS)
    async def join_scrim(self, ctx, title: str, password: str):
        query_data = {
            "title": title
        }
        check_for_lobby = requests.get(
            f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=query_data)
        if check_for_lobby.status_code == 200:
            login_data = {
                "username": ctx.user.name,
                "password": password
            }
            login = requests.post(
                f"http://{API_BASE_URL}:{API_PORT}/login", data=login_data)
            if login.status_code == 200:
                auth = {
                    "Authorization": login.json()["token_type"] + " " + login.json()["token"]
                }
                join_lobby = requests.post(
                    f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=query_data, headers=auth)
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
        login = requests.post(
            f"http://{API_BASE_URL}:{API_PORT}/login", data=login_data)
        if login.status_code == 200:
            auth = {
                "Authorization": login.json()["token_type"] + " " + login.json()["token"]
            }
            leave_lobby = requests.delete(
                f"http://{API_BASE_URL}:{API_PORT}/reenit/", headers=auth)
            if leave_lobby.status_code == 200:
                await ctx.send(f"{ctx.user.name} left")
            elif leave_lobby.status_code == 409:
                await ctx.send("currently not in a lobby", delete_after=15)
            else:
                await ctx.send("error leaving scrim system", delete_after=15)
        else:
            await ctx.send("login failure", delete_after=15)

    @nextcord.slash_command(name="host", description="host scrim", guild_ids=TESTING_GUILD_IDS)
    async def host(self, ctx, title: str):
        data = {
            "title": title
        }
        check_for_lobby = requests.get(
            f"http://{API_BASE_URL}:{API_PORT}/reenit/scrim/", json=data)
        if check_for_lobby.status_code == 404:
            await ctx.send("no such lobby", delete_after=15)
        check_ownership = requests.get(
            f"http://{API_BASE_URL}:{API_PORT}/users/user", json={"username": ctx.user.name})
        owner_id = check_ownership.json()["id"]
        if check_for_lobby.status_code == 200 and owner_id != check_for_lobby.json()["lobby"]["owner_id"]:
            await ctx.send("only the owner can host", delete_after=15)
        if check_for_lobby.status_code == 200:
            view = ScrimLobby(title, ctx.user.name)
            await ctx.send(f"hosting {title}", delete_after=5)
            await ctx.send(title, view=view, delete_after=600)
            status = await view.wait()
            if status == False:
                await ctx.send(f"Error hosting {title}", delete_after=25)

    @nextcord.slash_command(name="register_account", description="register", guild_ids=TESTING_GUILD_IDS)
    async def register(self, ctx, password: str, steam64: str):
        validity_check = SteamID(steam64).is_valid()
        if validity_check == False:
            steam64 = steam64_from_url(steam64)
        if steam64 is not None or validity_check == True:
            user = {"username": ctx.user.name,
                    "password": password, "steam64": int(steam64)}
            user_registration = requests.post(
                f"http://{API_BASE_URL}:{API_PORT}/users/", json=user)
            if user_registration.status_code == 201:
                await ctx.send(f"{ctx.user.name} has been registered", delete_after=15)
            if user_registration.status_code == 400:
                await ctx.send(f"{ctx.user.name} has already registered", delete_after=15)
        else:
            await ctx.send("invalid steam64")

    @nextcord.slash_command(name="prunee", description="prune_members", guild_ids=TESTING_GUILD_IDS)
    async def prune(self, ctx):
        users = []
        channel = await self.bot.fetch_channel(923250717823746108)
        messages = await channel.history(limit=200).flatten()
        for message in messages:
            if message.author.name == "Puntari":
                await message.delete()
        # messages = await channel.history(limit=123).flatten()


def setup(bot):
    bot.add_cog(scrim(bot))
