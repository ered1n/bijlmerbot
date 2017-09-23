import os
from pathlib import Path
import requests
import filecmp
from datetime import date

DIR = os.path.dirname(os.path.realpath(__file__)) + "/"

WEEK = str(date.today().isocalendar()[1])
URL = "https://rooster.talnet.nl/zuidoost/" + WEEK + "/c/c00045.htm"
STATUS = ["old", "new"]
SCHEDULE_OLD_EXISTS = Path(DIR + "schedule_old.txt").is_file()
removeDates = "\n8.00"
isNotSchedule = False

def getSchedule(url):
    try:
        return requests.get(url).text.split(removeDates)[1]
    except IndexError:
        global isNotSchedule
        isNotSchedule = True
        return requests.get(url).text

def writeSchedule(status):
    filename = DIR  + "schedule_" + status + ".txt"
    with open(filename, "w") as txt_file:
        txt_file.write(getSchedule(URL))

def compare():
    return filecmp.cmp(DIR + "schedule_old.txt", DIR + "schedule_new.txt")

def runScript():
    if(not SCHEDULE_OLD_EXISTS):
        writeSchedule(STATUS[0])

    writeSchedule(STATUS[1])

    if(not isNotSchedule):
        if(not compare()):
            writeSchedule(STATUS[0])
            return True
        else:
            return False
    else:
        writeSchedule(STATUS[0])
        return False