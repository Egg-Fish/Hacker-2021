import os, sys
import logging
import time
import math

from flask import Flask, request, session, render_template, redirect
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

def addGame(gamecode,
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

def createTestGame():
    addGame("oriontestgame", socketio)

    testPlayer = Player("TEST")
    testPlayer.setAlias("TEST")

    for i in range(1, 7):
        dummy = Player(f"dummy{i}")
        GAMES["oriontestgame"]["GameController"].addPlayer(dummy)

    GAMES["oriontestgame"]["GameController"].addMessage(testPlayer, "Testing Public Message")

    printGameInstance(GAMES["oriontestgame"]["GameInstance"])
    printGameController(GAMES["oriontestgame"]["GameController"])

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

socketio = SocketIO(app, async_mode="eventlet")

createTestGame()


if __name__=="__main__":
    # socketio.run(app=app, host="0.0.0.0", port=80, debug=True)
    pass