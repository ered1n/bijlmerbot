import os
from pathlib import Path
from datetime import date
import aiohttp
import asyncio
import hashlib

dir = os.path.dirname(os.path.realpath(__file__)) + "/"

week = str(date.today().isocalendar()[1])
url = "https://rooster.talnet.nl/zuidoost/" + week + "/c/c00044.htm"
old_exists = Path(dir + "old.txt").is_file()
filename = dir  + "old.txt"
removeDates = "\n8.00"

async def getSchedule():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                source = await response.text()
                return source.split(removeDates)[1]
    except IndexError:
        return False
        
def computeMD5hash(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

async def writeSchedule():
    with open(filename, "w") as data:
        data.write(computeMD5hash(await getSchedule()))
    
async def compare():
    with open(filename, "r") as data:
        md5_old = data.read()
    md5_new = computeMD5hash(await getSchedule())
    if md5_old == md5_new:
        return True
    else:
        return False

async def runScript():
    if not old_exists:
        await writeSchedule()
    if await getSchedule():
        if not await compare():
            await writeSchedule()
            return True
        else:
            return False
    else:
        return False