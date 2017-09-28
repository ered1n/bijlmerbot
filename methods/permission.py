import discord
from discord.ext import commands
from methods import permission
import json

def getPermissions(permissionJSON):
    with open(permissionJSON, "r") as data:
            return json.load(data)
            
def findPermission(permissions, cmd, server, roleOrUser):
    for rule in permissions:
        if rule["command"] == cmd and rule["server"] == server and rule["role/user"] == roleOrUser.id:
            return rule
    return False
    
def checkPermission(ctx):
    for rule in getPermissions(ctx.bot.permissionJSON):
        roles = []
        for role in ctx.author.roles:
            roles.append(role.id)
        if(rule["command"] == ctx.command.name and rule["server"] == ctx.guild.id):
            if(rule["role/user"] == ctx.author.id):
                return True
            elif(rule["role/user"] in roles):
                return True
    return False