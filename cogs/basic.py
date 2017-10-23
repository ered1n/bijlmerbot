import discord
import datetime

from discord.ext import commands
from methods import levels
from methods import permission

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

    #levels
    @commands.group()
    async def rank(self, ctx):
        if ctx.message.content == "$rank":
            xp = await self.bot.db.fetchone(f"SELECT xp FROM level WHERE user_id={ctx.author.id} AND server_id={ctx.guild.id}")
            await ctx.send("Your level is " + str(levels.get_level_from_xp(xp[0])) + " and your total xp is " + str(xp[0]))

    @rank.command()
    async def mention(self, ctx):
        mention = await self.bot.db.fetchone(f"SELECT mention FROM level WHERE user_id={ctx.author.id} AND server_id={ctx.guild.id}")
        if mention[0] == 0:
            await self.bot.db.execute(f"UPDATE level SET mention=1 WHERE user_id={ctx.author.id} AND server_id={ctx.guild.id}")
            await ctx.send("Level up mentions enabled")
        elif mention[0] == 1:
            await self.bot.db.execute(f"UPDATE level SET mention=0 WHERE user_id={ctx.author.id} AND server_id={ctx.guild.id}")
            await ctx.send("Level up mentions disabled")

    @rank.command()
    @commands.check(permission.checkPermission)
    async def channel(self, ctx, channel: int=None):
        server_exists = await self.bot.db.fetchone(f"SELECT * FROM server WHERE server_id={ctx.guild.id}")
        if not server_exists:
            if channel:
                await self.bot.db.execute(f"INSERT INTO server (server_id, rank_channel_id) VALUES ({ctx.guild.id}, {channel})")
            else:
                await self.bot.db.execute(f"INSERT INTO server (server_id, rank_channel_id) VALUES ({ctx.guild.id}, NULL)")
            await ctx.send("Level up notification channel set :thumbsup:")
        else:
            if channel:
                await self.bot.db.execute(f"UPDATE server SET rank_channel_id={channel} WHERE server_id={ctx.guild.id}")
            else:
                await self.bot.db.execute(f"UPDATE server SET rank_channel_id=NULL WHERE server_id={ctx.guild.id}")
            await ctx.send("Level up notification channel set :thumbsup:")

    @rank.command()
    async def leaderboard(self, ctx):
        data = await ctx.bot.db.fetch(f"SELECT user_id, xp FROM level WHERE server_id={ctx.guild.id} ORDER BY xp DESC")
        output = "```"
        for x in range(0, 50):
            try:
                output += "\n#" + str(x + 1) + " | " + str(await commands.MemberConverter().convert(ctx, str(data[x][0]))) + " | lvl: " + str(levels.get_level_from_xp(data[x][1])) + " | xp: " + str(data[x][1])
            except commands.BadArgument:
                pass
        await ctx.send(output + "```")

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(color=0x00ff00)
        embed.add_field(name="Invite me to your server", value="[Invite](https://discordapp.com/oauth2/authorize?client_id=327170106318651392&scope=bot)", inline=False)
        embed.add_field(name="Join my server", value="[Join](https://discord.gg/n7H8f5T)", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Basic(bot))