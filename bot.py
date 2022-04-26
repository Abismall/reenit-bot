from nextcord.ext import commands
import os
from dotenv import load_dotenv
from botconfig import botPrefix, requiredEnv
load_dotenv()
extensions = ["cogs.scrim"]
bot = commands.Bot(command_prefix=botPrefix)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    if __name__ == '__main__':
        bot.remove_command('help')
        for ext in extensions:
            bot.load_extension(ext)
        for guild in bot.guilds:
            try:
                await guild.rollout_application_commands()
            except:
                pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(error)
        return
if __name__ == '__main__':
    bot.run(os.getenv(requiredEnv["csgoscrimbot"]["bot_token"]))
