import os, sys
import logging
import time
import math

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

def testMessages():
    addGame("testmessages", socketio)

    # 1) Players join the game
    for i in range(1, 7):
        dummy = Player(f"dummy{i}")
        GAMES["testmessages"]["GameController"].addPlayer(dummy)

    # 2) Game Starts
    GAMES["testmessages"]["GameController"].startGame()
    # 2.1) This will not appear
    GAMES["testmessages"]["GameController"].handleMessage("maliciousfellow", "This will not appear")
    # 2.2) And these will appear in the respective chats
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "This will appear on the hacker chat, but will be erased")
    GAMES["testmessages"]["GameController"].handleMessage("dummy2", "This will appear on the whitehat chat, but will be erased")
    GAMES["testmessages"]["GameController"].handleMessage("dummy3", "This will appear on the investigator chat, but will be erased")
    GAMES["testmessages"]["GameController"].handleMessage("dummy4", "This wouldve appeared on the civilian chat, but its nighttime")
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "/t 2")
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "/t -1")
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "/t 0")
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "/t 3")

    GAMES["testmessages"]["GameController"].handleMessage("dummy2", "/p 3")
    GAMES["testmessages"]["GameController"].handleMessage("dummy2", "/p -1")
    GAMES["testmessages"]["GameController"].handleMessage("dummy2", "/p 0")
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "/p 3")

    GAMES["testmessages"]["GameController"].handleMessage("dummy3", "/s 2")
    GAMES["testmessages"]["GameController"].handleMessage("dummy3", "/s -1")
    GAMES["testmessages"]["GameController"].handleMessage("dummy3", "/s 0")
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "/s 3")

    printGameController(GAMES["testmessages"]["GameController"])
    # time.sleep(3)

    GAMES["testmessages"]["GameController"].updateGame()
    # 3) Night Ends. Everyone can talk
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "This will appear from dummy1's alias")
    
    GAMES["testmessages"]["GameController"].handleMessage("dummy2", "This will appear from dummy2's alias")
    GAMES["testmessages"]["GameController"].handleMessage("dummy3", "This will appear from dummy3's alias")
    GAMES["testmessages"]["GameController"].handleMessage("dummy4", "Now I can talk because it is daytime")
    GAMES["testmessages"]["GameController"].handleCommand("GAMEMASTER", "sendMessage:Gamemasters can talk to everyone")
    GAMES["testmessages"]["GameController"].handleMessage("andsomeone", "who is not in the game cannot talk")
    GAMES["testmessages"]["GameController"].handleCommand("andneither", "can they send commands")

    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "/v 0")
    GAMES["testmessages"]["GameController"].handleMessage("dummy1", "/v 1")
    GAMES["testmessages"]["GameController"].handleMessage("dummy2", "/v 4")
    GAMES["testmessages"]["GameController"].handleMessage("dummy3", "/v 1")
    GAMES["testmessages"]["GameController"].handleMessage("dummy4", "/v 1")
    GAMES["testmessages"]["GameController"].handleMessage("dummy5", "/v 5")
    GAMES["testmessages"]["GameController"].handleMessage("dummy6", "/v 5")

    printGameController(GAMES["testmessages"]["GameController"])
    # time.sleep(3)

    GAMES["testmessages"]["GameController"].updateGame()

    printGameInstance(GAMES["testmessages"]["GameInstance"])
    printGameController(GAMES["testmessages"]["GameController"])

def createTestSocket():
    addGame("testsocket", socketio)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

socketio = SocketIO(app, async_mode="eventlet")

# testMessages()
createTestSocket()

@app.route("/testsocket")
def testSocket():
    return render_template("testsocket.html")

@app.route("/socket/socket.io.js")
def sendSocketLibrary():
    return send_file("socket/socket.io.js")

@socketio.event
def testSocket():
    join_room("sussybaka")
    GAMES["testsocket"]["SocketController"].sendDataToRoom("SKRT", "sussybaka", "reloadPage")


if __name__=="__main__":
    socketio.run(app=app, host="0.0.0.0", port=80, debug=True)
    pass