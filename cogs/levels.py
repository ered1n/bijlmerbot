import discord
from discord.ext import commands
import time

class Levels:

    def __init__(self, bot):
        self.bot = bot

    def get_level_from_xp(self, xp):
        lvls_xp = [5 * (i ** 2) + 50 * i + 100 for i in range(200)]
        remaining_xp = int(xp)
        lvl = 0
        while remaining_xp >= lvls_xp[lvl]:
            remaining_xp -= lvls_xp[lvl]
            lvl += 1
        return lvl

    async def on_message(self, msg):
        user_exists = await self.bot.db.fetchone(f"SELECT * FROM user WHERE user_id='{msg.author.id}'")
        if not user_exists:
            create_user = await self.bot.db.execute(f"INSERT INTO user(user_id, server_id, xp, cooldown) VALUES({msg.author.id}, {msg.guild.id}, 0, NOW())")
            print("insert")

def setup(bot):
    bot.add_cog(Levels(bot))