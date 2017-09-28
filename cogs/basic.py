import discord
from discord.ext import commands
import datetime

class Basic:

    startTime = datetime.datetime.utcnow()

    def __init__(self, bot):
        self.bot = bot
    
    #ping
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong! :ping_pong:```" + str(round(self.bot.latency * 1000)) + "ms```")
    
    #uptime
    @commands.command()
    async def uptime(self, ctx):
        await ctx.send("The uptime is: ```" + str(datetime.datetime.utcnow() - self.startTime)[:-7] + "```")
        
def setup(bot):
    bot.add_cog(Basic(bot))