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
    if ctx.command.name == "add" or ctx.command.name == "remove":
        ctx.command.name = "perm"

    for rule in getPermissions(ctx.bot.permissionJSON):
        roles = []
        for role in ctx.author.roles:
            roles.append(role.id)
        if(rule["command"] == ctx.command.name and rule["server"] == ctx.guild.id):
            if(rule["role/user"] == ctx.author.id):
                return True
            elif(rule["role/user"] in roles):
                return True
    if (ctx.author.id == ctx.guild.owner.id):
        return True

    return False