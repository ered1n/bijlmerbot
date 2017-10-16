import discord
from discord.ext import commands
from schedule import schedule
from pathlib import Path
import asyncio
import time
import config
import sys, traceback
import os

bot = commands.Bot(command_prefix=config.prefix, help_attrs=dict(hidden=True))
bot.permissionJSON = os.path.dirname(os.path.realpath(__file__)) + "/permissions.json"
permissions_exist = Path(os.path.dirname(os.path.realpath(__file__)) + "/permissions.json").is_file()

cogs = ["cogs.basic", "cogs.moderation"]
            
bot.permCommands = ["perm", "purge"]

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
        
async def checkSchedule():
    await bot.wait_until_ready()
    while not bot.is_closed():
        if await schedule.runScript():
            roosterEmbed = discord.Embed(title="Roosterwijziging!", description="Het rooster is gewijzigd, klik [hier](" + schedule.url + ") voor de wijzigingen", colour=0xff0000)
            date = time.strftime("%d/%m/%Y %H:%M")
            roosterEmbed.set_footer(text=date)
            await bot.get_channel(359766050461450240).send("@everyone ", embed=roosterEmbed)
        await asyncio.sleep(60)

bot.loop.create_task(checkSchedule())
bot.run(config.key)
