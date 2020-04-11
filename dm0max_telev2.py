try:
	import json
	import telegram
	import logging
	import socket
	import time
	from geopy import distance
	from geopy import Point
	from datetime import datetime
except Exception as e:
	f= open("/home/pi/Crons/guru99.txt","w+")
	f.write(str(e))
	f.close()
	exit()

data = None
bottokenfile = open("/home/pi/Crons/bottoken.txt","r")
bottoken = bottokenfile.read().strip()
print(bottoken)
# In welchem Intervall soll man wieder für ein Flugzeug benachrichtigt werden (SEKUNDEN)
SHOUTINTERVALL = 1800  # halbe Stunde 1800

# Empfänger Position
receiverpos = Point("52.290542 8.701938")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
handler = logging.FileHandler("/home/pi/Crons/telegram.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Helikopter
heli_maxheight = 100  # meters
heli_maxvelocity = 60  # kilometer

# Flugzeuge die ausgegeben wurden
planes = []
planesNearChecked = []

# HEX von Flugzeugen, die zwar ausgegeben wurden, aber noch zu wenig Daten hatten
planesWFD = []  # WFD = WaitingForData

# Militärische Hubschrauber
bueckeburg = ["HELI264", "HELI911", "HELI646", "HELI942", "HELI955", "HELI922", "HELI652", "HELI942", "HELI332",
              "HELI605", "HELI950", "HELI901", "HELI417", "HELI332"]

bot = telegram.Bot(token=bottoken)
# bot.send_message(-254257027, text='Empfängerbot ist online.!')

def __init__(self):
    logger.info("Initalize...")


def planeToMessage(flugzeug, besondererText):
    logger.debug("Bereite Nachricht vor für " + flugzeug["hex"] + "|" + flugzeug["flight"])
    planeAlreadyShouted = False
    flugzeug["shouttime"] = datetime.now()

    if flugzeug["hex"] in planesWFD and "lat" in flugzeug:
        # Wenn Positionsdaten Verfügbar sind, dann ist gut!
        messageToTelegram(flugzeug, "Mehr Infos zu " + flugzeug["flight"])
        planesWFD.remove(flugzeug["hex"])
        return

    for plane in planes:
        if plane["hex"] == flugzeug["hex"]:
            # Das Flugzeug wurde schonmal gesendet
            logger.debug("Flugzeug wurde schonmal gesendet: " + flugzeug["hex"] + "|" + flugzeug["flight"])
            planeAlreadyShouted = True
            # Zeit überprüfen ob man wieder senden sollte...
            delta = flugzeug["shouttime"] - plane["shouttime"]
            logger.debug(
                "Flugzeug " + flugzeug["hex"] + "|" + flugzeug["flight"] + " wartet auf Intervall: " + str(delta))
            if delta.seconds > SHOUTINTERVALL:
                logger.debug(
                    "Intervall abgelaufen für " + flugzeug["hex"] + "|" + flugzeug["flight"] + " Sende neue Nachricht!")
                # Letzter Shout ist schon etwas her
                planes.remove(plane)
                planes.append(flugzeug)
                messageToTelegram(flugzeug, besondererText)
    if not planeAlreadyShouted:
        logger.debug("Flugzeug " + flugzeug["hex"] + "|" + flugzeug["flight"] + " wurde noch nicht gesendet")
        planes.append(flugzeug)
        messageToTelegram(flugzeug, besondererText)


def checkHelicopter(flugzeug):
    planeAlreadyShouted = False
    flugzeug["shouttime"] = datetime.now()

    if "altitude" in flugzeug and "speed" in flugzeug:
        if feetInMeters(flugzeug["altitude"]) < heli_maxheight and knotsInKms(flugzeug["speed"]) < heli_maxvelocity:
            for heli in planesNearChecked:
                if heli["hex"] == flugzeug["hex"]:
                    logger.debug("Helikopter wurde schonmal gesendet. " + flugzeug["hex"] + "|" + flugzeug["flight"])
                    planeAlreadyShouted = True
                    # Zeit überprüfen ob man wieder senden sollte...
                    delta = flugzeug["shouttime"] - heli["shouttime"]
                    logger.debug(
                        "Flugzeug " + flugzeug["hex"] + "|" + flugzeug["flight"] + " wartet auf Intervall: " + str(delta))
                    if delta.seconds > SHOUTINTERVALL:
                        logger.debug(
                            "Intervall abgelaufen für " + flugzeug["hex"] + "|" + flugzeug["flight"] + " Sende neue Nachricht!")
                        # Letzter Shout ist schon etwas her
                        planesNearChecked.remove(heli)
                        planesNearChecked.append(flugzeug)
                        print(flugzeug, "verdächtig tief")
                        messageToTelegram(flugzeug, "Flugobjekt fliegt verdächtig tief und langsam...")

            if not planeAlreadyShouted:
                logger.debug("Flugzeug " + flugzeug["hex"] + "|" + flugzeug["flight"] + " wurde noch nicht gesendet")
                planesNearChecked.append(flugzeug)
                print("Heli noch nicht gesendet "+flugzeug["hex"]+" "+str(flugzeug["altitude"]) + " " + str(flugzeug["speed"]))
                messageToTelegram(flugzeug, "Flugobjekt fliegt verdächtig tief und langsam...")


def feetInMeters(feets):
    return feets*0.3048

def knotsInKms(knots):
    return knots*1.852

def messageToTelegram(flugzeug, besondererText):
    nachricht = besondererText
    nachricht += "\nHEX:" + flugzeug["hex"]
    if "flight" in flugzeug:
        nachricht += "\nName: " + flugzeug["flight"]
    if "squawk" in flugzeug:
        nachricht += "\nSquawk: " + flugzeug["squawk"]
    if "speed" in flugzeug:
        nachricht += "\nGeschwindigkeit: " + str(round(int(flugzeug["speed"]) * 1.852)) + "km/h"
    if "altitude" in flugzeug:
        nachricht += "\nHöhe: " + str(round(int(flugzeug["altitude"]) / 3.28084)) + "m"
    if "lat" in flugzeug and "lon" in flugzeug:
        planepos = Point(str(flugzeug["lat"]) + " " + str(flugzeug["lon"]))
        rxdistance = round(distance.distance(receiverpos, planepos).kilometers, 3)
        nachricht += "\nEntfernung: " + str(rxdistance) + "km"
    else:
        planesWFD.append(flugzeug["hex"])
    nachricht += "\n"

    if "vert_rate" in flugzeug:
        nachricht += "\nVertikale Geschw.: " + str(round(int(flugzeug["vert_rate"]) / (3.28084 * 60), 2)) + "m/s"
    if "track" in flugzeug:
        nachricht += "\nFlugrichtung: " + str(flugzeug["track"]) + "°"
    if "rssi" in flugzeug:
        nachricht += "\nRSSI: " + str(flugzeug["rssi"]) + "dBFS"

    logger.info("Sende Nachricht:\n" + nachricht)

    nachricht += "\nhttps://dm0max.3ef.de/"
    try:
        bot.send_message(-254257027, text=nachricht)
        logger.debug("Sende eine Nachricht an Telegram: " + nachricht)
        if "lat" in flugzeug and "lon" in flugzeug:
            logger.debug("Sende Position: " + str(flugzeug["lat"]) + " " + str(flugzeug["lon"]))
            bot.sendLocation(-254257027, latitude=str(flugzeug["lat"]), longitude=str(flugzeug["lon"]))
    except Exception as e:
        logger.error("Beim senden einer Telegram Nachricht: " + str(e))
    print(nachricht)


def retrieveData():
    global data
    try:
        logger.debug("Lese Datei ein")
        file = open("/run/dump1090-mutability/aircraft.json")
        #file = open("aircraft.json")
        file = file.read()
        logger.debug("Datei eingelesen")
    except Exception as e:
        logger.error("Fehler beim Datei einlesen: " + str(e))
    data = json.loads(file)


logger.info("Initalized")
while True:
    logger.debug("Starte Durchlauf...")
    retrieveData()
    if "aircraft" in data:
        for plane in data["aircraft"]:
            if "flight" in plane:
                if plane["flight"][0:6] == "HUMMEL":
                    planeToMessage(plane, "Polizeihubschrauber")
                    #checkHelicopter(plane)
                    continue
                if plane["flight"][0:3] == "BPO":
                    planeToMessage(plane, "Bundespolizei")
                    continue
                if plane["flight"][0:3] == "CHX":
                    planeToMessage(plane, "Rettungshubschrauber - Christoph")
                    continue
                    #checkHelicopter(plane)
                if plane["flight"].strip() in bueckeburg:
                    #checkHelicopter(plane)
                    planeToMessage(plane, "BW Heeresflieger - möglw. Bückeburg")
                    continue
                if plane["flight"][0:3] == "FCK":
                    planeToMessage(plane, "Flightchecker - Deutsches Zentrum für Luft- und Raumfahrt")
                    continue
                if plane["flight"][0:3] in ["GAF","GAM","GNY"]:
                    planepos = Point(str(plane["lat"]) + " " + str(plane["lon"]))
                    rxdistance = round(distance.distance(receiverpos, planepos).kilometers, 3)
                    if rxdistance < 15:
                        if plane["flight"][0:3] == "GAF":
                            planeToMessage(plane, "German Air Force - LUFTWAFFE")
                        if plane["flight"][0:3] == "GAM":
                            planeToMessage(plane, "German Army - Bundeswehr")
                        if plane["flight"][0:3] == "GNY":
                            planeToMessage(plane, "German Navy - Bundeswehr")

    logger.debug("Warte etwas...")
    time.sleep(5)
