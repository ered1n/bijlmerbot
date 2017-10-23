import discord
import datetime
import math

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
    async def leaderboard(self, ctx, page: int=1):
        data = await ctx.bot.db.fetch(f"SELECT user_id, xp FROM level WHERE server_id={ctx.guild.id} ORDER BY xp DESC")
        amount_per_page = 10
        page = page - 1
        output = "```"
        if page < 0 or page * amount_per_page >= len(data):
            await ctx.send("Error, page doesn't exist :disappointed_relieved:")
        else:
            data_page = []
            counter = 1
            for x in range(len(data)):
                if x >= page * amount_per_page:
                    if x >= page * amount_per_page + amount_per_page:
                        break
                    try:
                        user = await commands.MemberConverter().convert(ctx, str(data[x][0]))
                        data_page.append(["#" + str(page * amount_per_page + counter), user.display_name, str(levels.get_level_from_xp(data[x][1])), str(data[x][1])])
                        counter += 1
                    except commands.BadArgument:
                        data_page.append(["#" + str(page * amount_per_page + counter), str(data[x][0]), str(levels.get_level_from_xp(data[x][1])), str(data[x][1])])
                        counter += 1
            for x in range(len(data_page)):
                output += "\n" + f"{data_page[x][0]:<{max(len(x[0]) for x in data_page)}}" + " | " + f"{data_page[x][1]:<{max(len(x[1]) for x in data_page)}}" + " | lvl: " + f"{data_page[x][2]:<{max(len(x[2]) for x in data_page)}}" + " | xp: " + data_page[x][3]
            await ctx.send(output + "\n\npage " + str(page + 1) + "/" + (str(math.ceil(len(data) / amount_per_page))) + "```")

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(color=0x00ff00)
        embed.add_field(name="Invite me to your server", value="[Invite](https://discordapp.com/oauth2/authorize?client_id=327170106318651392&scope=bot)", inline=False)
        embed.add_field(name="Join my server", value="[Join](https://discord.gg/CF7ArqD)", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Basic(bot))