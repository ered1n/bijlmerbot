from discord.ext import commands
import random


class Fun:

    def __init__(self, bot):
        self.bot = bot
        self.items = [[":apple:", 2.5], [":pear:", 2.6], [":tangerine:", 3.2], [":lemon:", 3.4],  [":strawberry:", 3.6]]

def setup(bot):
    bot.add_cog(Fun(bot))