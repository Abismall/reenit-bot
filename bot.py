from nextcord.ext import commands
import nextcord
import os
from dotenv import load_dotenv
from botconfig import botPrefix, requiredEnv
load_dotenv()
extensions = ["cogs.scrim"]
intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=botPrefix, intents=intents)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    channel = await bot.fetch_channel(923250717823746108)
    if __name__ == '__main__':
        bot.remove_command('help')
        for ext in extensions:
            bot.load_extension(ext)
        for guild in bot.guilds:
            try:
                await guild.rollout_application_commands()
            except:
                pass
        # guild = await bot.fetch_guild(696428646918914119, with_counts=True)
        # members = await guild.chunk()
        # for member in members:
        # if member.name not in users_to_keep:
        #     try:
        #         await guild.kick(member, reason="inactivity")
        #         await channel.send(
        #             f"{member.name}:lla ei vaaka näyttänyt 150kg", delete_after=5)
        #     except:
        #         print(f"ERROR KICKING {member.name}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(error)
        return
if __name__ == '__main__':
    bot.run(os.getenv(requiredEnv["csgoscrimbot"]["bot_token"]))
