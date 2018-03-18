import os
from pathlib import Path
import json
import sys

dial = int(sys.argv[1])
stop = sys.argv[2]
currentStation = sys.argv[3]


class RangeDict(dict):
    def __getitem__(self, item):
        if type(item) != range:  # or xrange in Python 2
            for key in self:
                if item in key:
                    return self[key]
        else:
            return super().__getitem__(item)

radioBands = RangeDict()


def changeStation(newStation, currentStation=None):
    """ Radio object to unmute.

    optionally pass a second Radio to mute, effectively
    "changing" from currentStation to newStation
    """
    if currentStation is None:
        unmute(newStation)
    else:
        mute(currentStation)
        unmute(newStation)


def monitorDial(dial, radioBands):
    global currentStation
    station = radioBands[dial]
    print(station.name)
    if station is currentStation:
        return "already playing"
    else:
        start(station)
        changeStation(station, currentStation)
        currentStation = station


class Radio(object):
    def __init__(radio, service='stereoio-mpr',
                 band=(90, 92), name="MPR News"):
        radio.socket = "/tmp/" + service + "-socket"
        radio.service = service
        radio.band = band
        radio.name = name


def running(radio):
    runningCommand = "systemctl is-active " + radio.service
    returnValue = os.system(runningCommand)
    return returnValue


def mute(radio):
    muteCommand = {"command": ("set_property", "mute", True)}
    returnValue = os.system("echo '" + json.dumps(muteCommand) + "' | socat - " + radio.socket)
    return returnValue


def unmute(radio):
    unmuteCommand = {"command": ("set_property", "mute", False)}
    echo = "echo '" + json.dumps(unmuteCommand) + "' | socat - " + radio.socket
    returnValue = os.system(echo)
    return returnValue


def cycleMute(radio):
    cycleMuteCommand = {"command": ("cycle", "mute")}
    echo = "echo '" + json.dumps(cycleMuteCommand) + "' | socat - " + radio.socket
    returnValue = os.system(echo)
    return returnValue


def start(radio):
    if running(radio) != 0:
        startCommand = "sudo systemctl start " + radio.service
        returnValue = os.system(startCommand)
        return returnValue
    else:
        return 0


def stop(radio):
    stopCommand = "sudo systemctl stop " + radio.service
    returnValue = os.system(stopCommand)
    return returnValue


def restart(radio):
    restartCommand = "sudo systemctl restart " + radio.service
    returnValue = os.system(restartCommand)
    return returnValue


json_data = open("stereoio.json").read()

radios = json.loads(json_data)

for radio in radios:
    # Pack the Radio class object into the radios dict
    radios[radio]["obj"] = Radio(radios[radio]["service"],
                                 radios[radio]["band"],
                                 radios[radio]["name"])
    # Create RangeDict of bands associated with radios.
    # Still not sure how to handle the "tuning" bands,
    radioBands[range(*radios[radio]["obj"].band)] = radios[radio]["obj"]
    start(radios[radio]["obj"])


def shutdown(radios):
    for radio in radios:
        stop(radios[radio]["obj"])

monitorDial(dial, radioBands)

if stop == "True":
    shutdown(radios)


print(str(currentStation.name))
sys.stdout.flush()
