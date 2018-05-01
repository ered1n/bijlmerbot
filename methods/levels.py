import discord
from discord.ext import commands
from methods import levels


def get_level_from_xp(xp):
    lvls_xp = [5 * (i ** 2) + 50 * i + 100 for i in range(200)]
    remaining_xp = int(xp)
    lvl = 0
    while remaining_xp >= lvls_xp[lvl]:
        remaining_xp -= lvls_xp[lvl]
        lvl += 1
    return lvl