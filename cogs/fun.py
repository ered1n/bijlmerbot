from discord.ext import commands
import random


class Fun:

    def __init__(self, bot):
        self.bot = bot
        self.items = [[":apple:", 2.5], [":pear:", 2.6], [":tangerine:", 3.2], [":lemon:", 3.4],  [":strawberry:", 3.6]]

    @commands.command()
    async def slots(self, ctx, bet: int = 10):

        if ctx.message.content != "$slots prizes":
            credit = await self.bot.db.fetchone(f"SELECT credits FROM level WHERE user_id={ctx.author.id} AND server_id={ctx.guild.id}")
            slot = []
            message = "you lost."
            prize = 0
            if credit[0] >= bet > 0:
                pickedItem = [self.items[0]] * 8 + [self.items[1]] * 6 + [self.items[2]] * 4 + [self.items[3]] + [self.items[4]]
                for x in range(0, 3):
                    random.shuffle(pickedItem)
                    slot.append(pickedItem[0])
                if slot[0] == slot[1] and slot[0] == slot[2]:
                    prize = round((bet * slot[0][1]) + bet)
                    message = "you won " + str(prize) + " credits!"
                else:
                    server_exists = await self.bot.db.fetchone(f"SELECT * FROM server WHERE server_id={ctx.guild.id}")
                    if not server_exists:
                        await self.bot.db.execute(f"INSERT INTO server (server_id, credits_spent) VALUES ({ctx.guild.id}, {bet})")
                    else:
                        credits_spent = await self.bot.db.fetchone(f"SELECT credits_spent FROM server WHERE server_id={ctx.guild.id}")
                        await self.bot.db.execute(f"UPDATE server SET credits_spent={credits_spent[0] + bet} WHERE server_id={ctx.guild.id}")
                await self.bot.db.execute(f"UPDATE level SET credits={(credit[0] - bet) + prize} WHERE user_id={ctx.author.id} AND server_id={ctx.guild.id}")
                await ctx.send(slot[0][0] + "|" + slot[1][0] + "|" + slot[2][0] + ", " + message + " You now have " + str((credit[0] - bet) + prize) + " credits, " + ctx.author.display_name)
            elif bet <= 0:
                await ctx.send("Nice try, but you can't do that " + ctx.author.display_name)
            else:
                await ctx.send("You're trying to place a bet of " + str(bet) + " credits, but you only have " + str(credit[0]) + ", " + ctx.author.display_name + " :cry:")

    @commands.command()
    async def prizes(self, ctx):
        output = "```"
        for x in range(len(self.items)):
            output += self.items[x][0] + " = bet * " + str(self.items[x][1]) + " + bet\n"
        await ctx.send(output + "```")

    @commands.command()
    async def credits(self, ctx):
        credit = await self.bot.db.fetchone(
            f"SELECT credits FROM level WHERE user_id={ctx.author.id} AND server_id={ctx.guild.id}")
        await ctx.send("You have " + str(credit[0]) + " credits, " + ctx.author.display_name + " :thumbsup:")


def setup(bot):
    bot.add_cog(Fun(bot))