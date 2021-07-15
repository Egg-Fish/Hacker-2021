import os, sys
import logging
import time
import math

from flask import Flask, request, session, render_template, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from gameinstance import GameInstance
from socketcontroller import SocketController
from gamecontroller import GameController

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

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

socketio = SocketIO(app, async_mode="eventlet")

addGame("oriontestgame", socketio)

if __name__=="__main__":
    socketio.run(app=app, host="0.0.0.0", port=80, debug=True)