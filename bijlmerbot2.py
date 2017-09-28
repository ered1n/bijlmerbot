import discord
from discord.ext import commands
import config
import sys, traceback
import os

bot = commands.Bot(command_prefix=config.prefix, help_attrs=dict(hidden=True))
bot.permissionJSON = os.path.dirname(os.path.realpath(__file__)) + "/permissions.json"

cogs = ["cogs.basic",
            "cogs.moderation"]
            
bot.permCommands = ["perm",
                                   "purge"]

@bot.event
async def on_ready():
    print("Bot online")
    print(bot.user.name)
    print(bot.user.id)
    print("-------------------")
    
    await bot.change_presence(game=discord.Game(name=config.prefix + "help", url="https://www.twitch.tv/bijlmerbot", type=1))
    
    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Failed to load cog {cog}.', file=sys.stderr)
            traceback.print_exc()
            
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Incorrect syntax, use ```" + config.prefix + "help <command>```")

bot.run(config.key)