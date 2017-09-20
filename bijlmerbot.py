import discord
import asyncio
import threading
import time
import datetime
import config
from schedule_notification import schedule_notification_discord

client = discord.Client()
startTime = datetime.datetime.utcnow()
prefix = config.prefix
date = time.strftime("%d/%m/%Y %H:%M")
roosterEmbed = discord.Embed(title="Roosterwijziging!", description="Het rooster is gewijzigd, klik [hier](" + schedule_notification_discord.URL + ") voor de wijzigingen", colour=0xff0000)
roosterEmbed.set_footer(text=date)
helpList = ["**Purge:** " + prefix + "purge <user*> <amount> - Deletes messages \n",
            "**Ping:** " + prefix + "ping - Checks latency of the bot\n",
            "**Uptime:** " + prefix + "uptime - Shows the uptime of the bot\n"]
helpEmbed = discord.Embed(title="Commands", description=helpList[0] + helpList[1] + helpList[2]  + "\n* is not required", colour=0x00ff00)
helpEmbed.set_footer(text=date)

@client.event
async def on_ready():
    print("bot online")
    await client.change_presence(game=discord.Game(name="$help", url="https://www.twitch.tv/bijlmerbot", type=1))
    while True:
        if(schedule_notification_discord.runScript()):
            await client.send_message(discord.Object(id="359766050461450240"), "@everyone ", embed=roosterEmbed)
        await asyncio.sleep(300)

@client.event
async def on_message(message):
    if(message.content.startswith(prefix)):
        cmd = message.content[len(prefix):].split(" ")[0]
        args = message.content.split(" ")[1:]

        #help
        if(cmd == "help"):
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

        #purge
        if(cmd == "purge"):
            length = len(args)
            if(length <= 2):
                if(length == 1):
                    try:
                        await client.purge_from(message.channel, limit=int(args[0]) + 1)
                        deleteEmbed = discord.Embed(title="Messages deleted", description="Deleted " + args[0] + " message(s)", colour=0x00ff00)
                        deleteEmbed.set_footer(text=date)
                        await client.send_message(message.channel, embed=deleteEmbed)
                    except discord.errors.HTTPException:
                        await client.send_message(message.channel, "Error deleting messages")
                elif(length == 2):
                    counter = 0
                    user_id = args[0].replace("<", "").replace("@", "").replace(">", "").replace("!", "")
                    await client.purge_from(message.channel, limit=1)
                    async for msg in client.logs_from(message.channel):
                        if(msg.author.id == user_id):
                            counter += 1
                            try:
                                await client.delete_message(msg)
                            except discord.errors.HTTPException:
                                await client.send_message(message.channel, "Error deleting messages")
                        if(counter >= int(args[1])):
                            break
                    deleteEmbed = discord.Embed(title="Messages deleted", description="Deleted " + str(counter) + " message(s)", colour=0x00ff00)
                    deleteEmbed.set_footer(text=date)
                    await client.send_message(message.channel, embed=deleteEmbed)
            else:
                await client.send_message(message.channel, "Error, the correct syntax is: ```$purge <user> <amount>```")

client.run(config.key)
