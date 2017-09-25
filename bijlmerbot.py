import discord
import asyncio
import threading
import time
import datetime
import config
import json
from schedule_notification import schedule_notification_discord

client = discord.Client()
startTime = datetime.datetime.utcnow()
prefix = config.prefix
permCommands = ["perm", "purge"]
purgeMax = 1000
roosterEmbed = discord.Embed(title="Roosterwijziging!", description="Het rooster is gewijzigd, klik [hier](" + schedule_notification_discord.URL + ") voor de wijzigingen", colour=0xff0000)
helpList = ["**Purge:** " + prefix + "purge <user^> <amount> - Deletes messages\n\n",
            "**Ping:** " + prefix + "ping - Checks latency of the bot\n\n",
            "**Uptime:** " + prefix + "uptime - Shows the uptime of the bot\n\n",
            "**Perm:** " + prefix + "perm <add/remove> <command> <role/user> - Add/remove permissions to a command^^\n\n"]
helpEmbed = discord.Embed(title="Commands", description=helpList[0] + helpList[1] + helpList[2]  + helpList[3]  + "^ is not required\n^^ can only be used by the server owner or those with permission", colour=0x00ff00)

def checkPermission(command, permissions, message):
    for rule in permissions:
        roles = []
        for role in message.author.roles:
            roles.append(role.id)
        roleOrUser = rule["role/user"].replace("<", "").replace("@", "").replace(">", "").replace("!", "").replace("&", "")
        if(rule["command"] == command and rule["server"] == message.server.id):
            if(roleOrUser == message.author.id):
                return True
            elif(roleOrUser in roles):
                return True
    return False

def findPermission(command, permissions, message, roleOrUser):
    for rule in permissions:
        if(rule["command"] == command and rule["server"] == message.server.id and rule["role/user"] == roleOrUser):
            return rule
    return False

async def deleteMessages(message, length, args, purgeValue):
    counter = 0
    if(length == 2):
        user_id = args[0].replace("<", "").replace("@", "").replace(">", "").replace("!", "")
    await client.purge_from(message.channel, limit=1)
    async for msg in client.logs_from(message.channel, limit=purgeMax):
        if(length == 1):
            counter += 1
            try:
                await client.delete_message(msg)
            except discord.errors.HTTPException:
                await client.send_message(message.channel, "Error deleting messages")
        if(counter >= purgeValue):
            break
        elif(length == 2):
            if(msg.author.id == user_id):
                counter += 1
                try:
                    await client.delete_message(msg)
                except discord.errors.HTTPException:
                    await client.send_message(message.channel, "Error deleting messages")
            if(counter >= purgeValue):
                break
    deleteEmbed = discord.Embed(title="Messages deleted", description="Deleted " + str(counter) + " message(s)", colour=0x00ff00)
    date = time.strftime("%d/%m/%Y %H:%M")
    deleteEmbed.set_footer(text=date)
    await client.send_message(message.channel, embed=deleteEmbed)

async def checkSchedule():
    await client.wait_until_ready()
    while not client.is_closed:
        if(schedule_notification_discord.runScript()):
            date = time.strftime("%d/%m/%Y %H:%M")
            roosterEmbed.set_footer(text=date)
            await client.send_message(discord.Object(id="359766050461450240"), "@everyone ", embed=roosterEmbed)
        await asyncio.sleep(60)
    
@client.event
async def on_ready():
    print("Bot online")
    print(client.user.name)
    print(client.user.id)
    print("-------------------")
    await client.change_presence(game=discord.Game(name=prefix + "help", url="https://www.twitch.tv/bijlmerbot", type=1))

@client.event
async def on_message(message):
    if(message.content.startswith(prefix)):
        cmd = message.content[len(prefix):].split(" ")[0]
        args = message.content.split(" ")[1:]
        permissions = []
        with open("permissions.json", "r") as data:
            permissions = json.load(data)

        #help
        if(cmd == "help"):
            date = time.strftime("%d/%m/%Y %H:%M")
            helpEmbed.set_footer(text=date)
            await client.send_message(message.channel, embed=helpEmbed)

        #ping
        if(cmd == "ping"):
            start = time.time()
            await client.send_message(message.channel, "Pong! :ping_pong:")
            stop = time.time() - start
            async for msg in client.logs_from(message.channel):
                if(msg.author.id == client.user.id):
                    await client.edit_message(msg, "Pong! :ping_pong: " + "```" + str(round(stop * 1000)) + "ms```")
                    break;

        #uptime
        if(cmd == "uptime"):
            uptime = datetime.datetime.utcnow() - startTime
            await client.send_message(message.channel, "The uptime is: ```" + str(uptime) + "```")

        #perm
        if(cmd == "perm"):
            if(message.author == message.server.owner or checkPermission(cmd, permissions, message)):
                if(len(args) == 3):
                    if(args[0] == "add" or args[0] == "remove"):
                        if(args[1] in permCommands):
                            if(args[0] == "add"):
                                if(not findPermission(args[1], permissions, message, args[2])):
                                    rule = {"command": args[1], "server": message.server.id, "role/user": args[2]}
                                    with open("permissions.json", "r+") as data:
                                        perms = json.load(data)
                                        perms.append(rule)
                                        data.seek(0)
                                        json.dump(perms, data)
                                    await client.send_message(message.channel, "Permission added :ok_hand: :100:")
                                else:
                                    await client.send_message(message.channel, "Error, this rule already exists :smirk:")
                            elif(args[0] == "remove"):
                                rule = findPermission(args[1], permissions, message, args[2])
                                if(rule):
                                    with open("permissions.json", "r+") as data:
                                        perms = json.load(data)
                                        perms.pop(perms.index(rule))
                                        data.seek(0)
                                        json.dump(perms, data)
                                        data.truncate()
                                    await client.send_message(message.channel, "Permission removed :worried:")
                                else:
                                    await client.send_message(message.channel, "Error, rule doesn't exist :rage:")
                        else:
                            await client.send_message(message.channel, "Error, command doesn't require permission or doesn't exist")
                    else:
                        await client.send_message(message.channel, "Error, the correct syntax is: ```$perm <add/remove> <command> <role/user>```")
                else:
                    await client.send_message(message.channel, "Error, the correct syntax is: ```$perm <add/remove> <command> <role/user>```")
            else:
                await client.send_message(message.channel, "Error, you don't have permission to use the " + cmd + " command")

        #purge
        if(cmd == "purge"):
            if(checkPermission(cmd, permissions, message)):
                length = len(args)
                if(length <= 2 and length >= 1):
                    if(length == 1):
                        purgeValue = int(args[0])
                    elif(length == 2):
                        purgeValue = int(args[1])
                    if(purgeValue <= purgeMax):
                        await deleteMessages(message, length, args, purgeValue)
                    else:
                        await client.send_message(message.channel, "Error, the max amount of messages you can delete is " + str(purgeMax))
                else:
                    await client.send_message(message.channel, "Error, the correct syntax is: ```$purge <user> <amount>```")
            else:
                await client.send_message(message.channel, "Error, you don't have permission to use the " + cmd + " command")

client.loop.create_task(checkSchedule())
client.run(config.key)