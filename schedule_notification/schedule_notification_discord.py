import os
from pathlib import Path
from datetime import date
import aiohttp
import asyncio
import hashlib

dir = os.path.dirname(os.path.realpath(__file__)) + "/"

week = str(date.today().isocalendar()[1])
url = "https://rooster.talnet.nl/zuidoost/" + week + "/c/c00044.htm"
schedule_old_exists = Path(dir + "schedule_old.txt").is_file()
filename = dir  + "schedule_old.txt"
removeDates = "\n8.00"

def getSchedule():
    try:
        request = yield from aiohttp.request("get", url)
        src = yield from request.text()
        return src.split(removeDates)[1]
    except IndexError:
        return False
        
def computeMD5hash(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

async def writeSchedule(client):
    with open(filename, "w") as data:
        data.write(computeMD5hash(await client.loop.create_task(getSchedule())))
    
async def compare(client):
    with open(filename, "r") as data:
        md5_old = data.read()
    md5_new = computeMD5hash(await client.loop.create_task(getSchedule()))
    if(md5_old == md5_new):
        return True
    else:
        return False

async def runScript(client):
    if(not schedule_old_exists):
        await writeSchedule(client)
    if(await client.loop.create_task(getSchedule())):
        if(not await compare(client)):
            await writeSchedule(client)
            return True
        else:
            return False
    else:
        return False