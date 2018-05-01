import discord
import time

from discord.ext import commands
from random import randint
from methods import levels

class Levels:

    def __init__(self, bot):
        self.bot = bot

    async def get_cooldown(self, msg):
        return await self.bot.db.fetchone("SELECT cooldown FROM users WHERE user_id={} AND server_id={}".format(msg.author.id, msg.guild.id))

    async def get_xp(self, msg):
        xp = await self.bot.db.fetchone("SELECT xp FROM users WHERE user_id={} AND server_id={}".format(msg.author.id, msg.guild.id))
        return xp[0]

    async def set_xp(self, msg, current_time):
        xp = await self.get_xp(msg)
        await self.bot.db.execute("UPDATE users SET xp={}, cooldown='{}' WHERE user_id={} AND server_id={}".format(xp + randint(15, 25), current_time, msg.author.id, msg.guild.id))

    async def on_message(self, msg):
        user_exists = await self.bot.db.fetchone("SELECT * FROM users WHERE user_id={} AND server_id={}".format(msg.author.id, msg.guild.id))
        if not user_exists:
            if not msg.author.bot:
                current_time = time.strftime("%d-%m-%Y %H:%M")
                await self.bot.db.execute("INSERT INTO users (user_id, server_id, xp, cooldown) VALUES ({}, {}, 0, '{current_time}')".format(msg.author.id, msg.guild.id))
        else:
            lvl_before = levels.get_level_from_xp(await self.get_xp(msg))
            cooldown = await self.bot.db.fetchone("SELECT cooldown FROM users WHERE user_id={} AND server_id={}".format(msg.author.id, msg.guild.id))
            current_time = time.strftime("%d-%m-%Y %H:%M")
            if cooldown[0] != current_time:
                await self.set_xp(msg, current_time)
            else:
                await self.bot.db.execute("UPDATE users SET cooldown='{}' WHERE user_id={} AND server_id={}".format(current_time, msg.author.id, msg.guild.id))
            lvl_after = levels.get_level_from_xp(await self.get_xp(msg))
            if(lvl_before != lvl_after):
                mention = await self.bot.db.fetchone("SELECT mention FROM users WHERE user_id={} AND server_id={}".format(msg.author.id, msg.guild.id))
                if mention[0] == 1:
                    rank_channel_id = await self.bot.db.fetchone("SELECT rank_channel_id FROM server WHERE server_id={}".format(msg.guild.id))
                    if not rank_channel_id[0]:
                        await msg.channel.send("Congratulations <@" + str(msg.author.id) + ">, you have advanced to level " + str(lvl_after))
                    else:
                        await self.bot.get_channel(rank_channel_id[0]).send("Congratulations <@" + str(msg.author.id) + ">, you have advanced to level " + str(lvl_after))

def setup(bot):
    bot.add_cog(Levels(bot))
