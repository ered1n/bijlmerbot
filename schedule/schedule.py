import os
from pathlib import Path
from datetime import date
import aiohttp
import asyncio
import hashlib

dir = os.path.dirname(os.path.realpath(__file__)) + "/"

nav = "https://rooster.talnet.nl/zuidoost/frames/navbar.htm"
old_exists = Path(dir + "old.txt").is_file()
filename = dir  + "old.txt"
removeDates = "\n8.00"
navTop = "var classes = "
navBot = "\n var teachers = "

def getWeek():
    return date.today().isocalendar()[1]

async def getClassNum():
    async with aiohttp.ClientSession() as session:
            async with session.get(nav) as response:
                source = await response.text()
                return eval(source.split(navTop)[1].split(navBot)[0].replace(";", "")).index("OITAOO5A") + 1
          
async def getSchedule():
    week = getWeek()
    classNum = await getClassNum()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://rooster.talnet.nl/zuidoost/{week}/c/c000{classNum}.htm") as response:
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
    if await getSchedule():
        if not old_exists:
            await writeSchedule()
        if not await compare():
            await writeSchedule()
            return True
        else:
            return False
    else:
        return False
