import os
from pathlib import Path
from datetime import date
import aiohttp
import asyncio
import hashlib

dir = os.path.dirname(os.path.realpath(__file__)) + "/"

nav = "https://rooster.talnet.nl/zuidoost/frames/navbar.htm"
url = ""
old_exists = Path(dir + "old.txt").is_file()
filename = dir  + "old.txt"
removeDates = "\n8.00"
navTop = "var classes = "
navBot = "\n var teachers = "

def getWeek():
    return date.today().isocalendar()[1]

async def getClassNum():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(nav) as response:
                source = await response.text()
                return eval(source.split(navTop)[1].split(navBot)[0].replace(";", "")).index("OITAOO5A") + 1
    except ConnectionResetError:
        return False
    except aiohttp.ClientOSError:
        return False

async def getSchedule():
    week = getWeek()
    classNum = await getClassNum()
    if not classNum:
        return False
    else:
        z = "0" * (5 - len(str(classNum)))
        global url
        url = "https://rooster.talnet.nl/zuidoost/{}/c/c{}{}.htm".format(week, z, classNum)
        try:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        source = await response.text()
                        return source.split(removeDates)[1]
            except ConnectionResetError:
                return False
            except aiohttp.ClientOSError:
                return False
        except IndexError:
            return False

def computeMD5hash(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

async def writeSchedule(schedule):
    with open(filename, "w") as data:
        data.write(computeMD5hash(schedule))

async def compare(schedule):
    with open(filename, "r") as data:
        md5_old = data.read()
    md5_new = computeMD5hash(schedule)
    if md5_old == md5_new:
        return True
    else:
        return False

async def runScript():
    schedule = await getSchedule()
    if schedule:
        if not old_exists:
            await writeSchedule(schedule)
        if not await compare(schedule):
            await writeSchedule(schedule)
            return True
        else:
            return False
    else:
        return False
