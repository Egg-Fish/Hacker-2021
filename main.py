"""
Hacker - StrITwise 2021: Edge of Automation
Hacker is a web-based game that was created for the event, 
StrITwise 2021: Edge of Automation for Ngee Ann Polytechnic.
Copyright (C) 2021 Eugenio Manansala, Richard Pamintuan, Wong Chao Hao

This file is part of Hacker.

Hacker is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Hacker is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Hacker.  If not, see <https://www.gnu.org/licenses/>.
"""
import os, sys
import logging
import time
import math
import string
import random

from flask import Flask, request, session, render_template, redirect, send_file
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from gameinstance import GameInstance, printGameInstance
from socketcontroller import SocketController
from gamecontroller import GameController, printGameController

from player import Player

GAMES = {}
"""dict[
    gamecode: {
        "GameInstance": GameInstance, 
        "GameController": GameController,
        "SocketController": SocketController
    }]
"""

os.system("mkdir logs")
logging.basicConfig(
    filename=f"logs/{int(time.time())}.log", 
    filemode="w+", 
    level=logging.DEBUG, 
    format="[%(asctime)s][%(module)s][%(funcName)s][%(levelname)s]: %(message)s")


def createGame(gamecode,
    socketio:SocketIO,
    maxHackers=1,
    maxWhitehats=1,
    maxInvestigators=1,
    aliasFilename="random_names.txt",):
    # Adds the GameInstance along with a GameController to GAMES

    gameinstance = GameInstance(
        gamecode,
        maxHackers,maxWhitehats,maxInvestigators,
        aliasFilename)

    socketcontroller = SocketController(gamecode, socketio)

    gamecontroller = GameController(gamecode, gameinstance, socketcontroller)

    GAMES[gamecode] = {
        "GameInstance": gameinstance, 
        "GameController": gamecontroller,
        "SocketController": socketcontroller
    }

    logging.info(f"Created game {gamecode} (MH: {maxHackers}, MW: {maxWhitehats}, MI: {maxInvestigators})")

def generateSID(size=24, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

socketio = SocketIO(app, async_mode="eventlet")


# Test Code

@app.route("/render/<path>")
def testRender(path):
    session["name"] = "test1"
    session["gamecode"] = "testgame"

    if path == "endscreen.html":
        GAMES["testgame"]["GameController"].startGame()
        return render_template(path, gi=GAMES["testgame"]["GameInstance"])

    return render_template(path)

createGame("testgame", socketio)
for i in range(1, 7):
    dummy = Player(f"test{i}")
    GAMES["testgame"]["GameController"].addPlayer(dummy)

createGame("oriontestgame", socketio)

@app.route("/test/addplayer")
def testAddPlayer():
    dummy = Player(f"newplayer")
    GAMES["testgame"]["GameController"].addPlayer(dummy)
    return "done"

@app.route("/test/removeplayer")
def testRemovePlayer():
    GAMES["testgame"]["GameController"].removePlayer("newplayer")
    return "done"

# Actual Code
@app.route("/socket/socket.io.js")
def sendSocketLibrary():
    return send_file("socket/socket.io.js")

@app.route("/favicon.ico")
def favicon():
    return send_file("favicons/favicon.ico")

@app.route("/")
def handleMain():
    if not "gamecode" in session:
        return render_template("joinscreen.html")
    else:
        name = session["name"]
        gamecode = session["gamecode"]

        gamestatus = GAMES[gamecode]["GameInstance"].getGameStatus()

        if gamestatus == 0:
            return render_template("waitingscreen.html")
        elif gamestatus == 1:
            return render_template("game.html")
        elif gamestatus == 2:
            return render_template("endscreen.html", gi=GAMES[gamecode]["GameInstance"])
        else:
            logging.error(f"User {name} in gamecode {gamecode} with gamestatus = {gamestatus} did not load a page.")
            return "OOPS"

@app.route("/joingame", methods=["POST"])
def joinGame():
    name = request.form["name"]
    gamecode = request.form["gamecode"]

    if gamecode in GAMES:
        session["name"] = name
        session["gamecode"] = gamecode

        player = Player(name)

        GAMES[gamecode]["GameController"].addPlayer(player)

    return redirect("/")

@app.route("/gm/<gamecode>")
def gamemasterScreen(gamecode):
    session["name"] = "GAMEMASTER"
    session["gamecode"] = gamecode

    return render_template("gamemasterscreen.html")


@socketio.on("connect")
def connect():
    if "gamecode" in session:
        name = session["name"]
        gamecode = session["gamecode"]
        SID = generateSID()

        join_room(f"{gamecode}/{SID}")
        join_room(f"{gamecode}")
        GAMES[gamecode]["SocketController"].addClientToController(name, SID)

@socketio.on("command")
def handleCommandToGameController(data):
    if "gamecode" in session:
        name = session["name"]
        gamecode = session["gamecode"]
        command = data

        logging.debug(f"Received command {command} from name {name} in game code {gamecode}")
        GAMES[gamecode]["GameController"].handleCommand(name, data)
    
@socketio.on("message")
def handleMessageToGameController(data):
    if "gamecode" in session:
        name = session["name"]
        gamecode = session["gamecode"]
        message = data

        logging.debug(f"Received message {message} from name {name} in game code {gamecode}")
        GAMES[gamecode]["GameController"].handleMessage(name, message)


if __name__=="__main__":
    host = sys.argv[1]
    port = sys.argv[2]

    socketio.run(app=app, host=host, port=port, debug=True)
    pass