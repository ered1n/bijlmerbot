import os
from pathlib import Path
import urllib.request
import filecmp
from datetime import date

DIR = os.path.dirname(os.path.realpath(__file__)) + "/"

WEEK = str(date.today().isocalendar()[1])
URL = "https://rooster.talnet.nl/zuidoost/" + WEEK + "/c/c00045.htm"
STATUS = ["old", "new"]
SCHEDULE_OLD_EXISTS = Path(DIR + "schedule_old.txt").is_file()


def getSchedule(url):
    try:
        return urllib.request.urlopen(url).read()
    except Exception as ex:
        return ex

def writeSchedule(status):
    filename = DIR  + "schedule_" + status + ".txt"
    with open(filename, "wb+") as txt_file:
        txt_file.write(getSchedule(URL))

def compare():
    return filecmp.cmp(DIR + "schedule_old.txt", DIR + "schedule_new.txt")

def runScript():
    if(not SCHEDULE_OLD_EXISTS):
        writeSchedule(STATUS[0])

    writeSchedule(STATUS[1])

    if(not compare()):
        writeSchedule(STATUS[0])
        return True
    else:
        return False
