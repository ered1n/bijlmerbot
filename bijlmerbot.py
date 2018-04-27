import discord
import asyncio
import time
import config
import sys, traceback
import os

from discord.ext import commands
from schedule import schedule
from pathlib import Path
from methods.db import DB

bot = commands.Bot(command_prefix=config.prefix, help_attrs=dict(hidden=True))
bot.permissionJSON = os.path.dirname(os.path.realpath(__file__)) + "/permissions.json"
bot.db = DB(config.db_host, config.db_user, config.db_pass, config.db_name, bot.loop)
permissions_exist = Path(os.path.dirname(os.path.realpath(__file__)) + "/permissions.json").is_file()

cogs = ["cogs.basic", "cogs.moderation", "cogs.levels"]
            
bot.permCommands = ["perm", "purge", "channel", "ban", "kick", "warn", "say"]


@bot.event
async def on_ready():
    print("Bot online")
    print("Discord.py version: " + discord.__version__)
    print(bot.user.name)
    print(bot.user.id)
    print("-------------------")

    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name='you sleep', type=discord.ActivityType.watching))

    await bot.db.connect()

    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Failed to load cog {cog}.', file=sys.stderr)
            traceback.print_exc()
    
    if not permissions_exist:
        with open(bot.permissionJSON, "w") as data:
            data.write("[]")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Incorrect syntax, use ```" + config.prefix + "help <command>```")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument(s) use ```" + config.prefix + "help <command>```")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("Error, you don't have permission to use the " + ctx.command.name + " command :rage:")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("Error, I can't " + ctx.command.name + " this user because I don't have permission or the user has a higher role :cry:")


async def checkSchedule():
    await bot.wait_until_ready()
    while not bot.is_closed():
        if await schedule.runScript():
            roosterEmbed = discord.Embed(title="Roosterwijziging!", description="Het rooster is gewijzigd, klik [hier](" + schedule.url + ") voor de wijzigingen", colour=0xff0000)
            date = time.strftime("%d/%m/%Y %H:%M")
            roosterEmbed.set_footer(text=date)
            await bot.get_channel(359766050461450240).send("@everyone ", embed=roosterEmbed)
        await asyncio.sleep(60)

#bot.loop.create_task(checkSchedule())
bot.run(config.key)
