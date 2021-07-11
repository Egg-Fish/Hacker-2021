import random
import time
import logging
import os

from flask import Flask, send_file, send_from_directory
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask import render_template, request, redirect, session

from game_logic import GameInstance, create_player, GAMES

logging.basicConfig(
    filename=f"logs\log.log", 
    filemode="w+", 
    level=logging.DEBUG, 
    format='[%(asctime)s][%(funcName)s][%(levelname)s]:%(message)s')

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
socketio = SocketIO(app, async_mode="eventlet")

# SocketIO Library
@app.route("/socket/socket.io.js")
def sendSocketIOFile():
    return send_file("socket/socket.io.js")
    


# TEST: REMOVE IN PRODUCTION
oriontestgame = GameInstance("oriontestgame", nHackers=2)
GAMES.update({"oriontestgame": oriontestgame})

dummygame = GameInstance("dummygame")

dummyplayer = create_player("dummy")
dummygame.add_player(dummyplayer)

GAMES.update({"dummygame": dummygame})

@app.route("/test/<path>")
def test(path):
    dummygame.startGame()
    session["name"] = "dummy"
    session["gamecode"] = "dummygame"
    session["role"] = "hacker"
    session["alias"] = "sussybaka"

    return render_template(path)

# Application Events
@app.route("/", methods=["POST", "GET"])
def game():
    host = request.host

    if request.method == "POST":
        name = request.form['name']
        gamecode = request.form['gamecode']

        if len(name.strip()) == 0 or len(gamecode.strip()) == 0:
            return render_template("joinscreen.html")

        else:
            session["name"] = name
            session["gamecode"] = gamecode

            player = create_player(name)
            game = GAMES[gamecode]
            game.add_player(player)

            return render_template("waitingscreen.html")

    else:
        if "gamecode" in session and "name" in session:
            game = GAMES[session["gamecode"]]
            if game.status == 0:
                return render_template("waitingscreen.html")

            if game.status == 1:
                return render_template("game.html")

            elif game.status == 2:
                return "The game has ended. Thank you for playing!"
        
        else:
            return render_template("joinscreen.html")



# Gamemaster Screen
@app.route("/gm/<gamecode>")
def gamemaster(gamecode):
    session["gamecode"] = gamecode
    return render_template("gamemaster.html")



# SocketIO Events
@socketio.on("connect")
def connect():
    host = request.host
    logging.debug(f"Host {host} has connected")

@socketio.on("disconnect")
def disconnect():
    host = request.host
    logging.debug(f"Host {host} has disconnected")

@socketio.on("startGame")
def startGame():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    game.startGame() # Initialises everything for the game to start

    emit("startGame", to=f"{gamecode}/player") # Sends a message to the players to refresh the page

@socketio.on("getGameData")
def getGameData():
    gamecode = session["gamecode"]
    game = GAMES[gamecode]

    data = game.getGameData()

    emit("gameData", data)

@socketio.on("joinGameRoom")
def joinGameRoom():
    gamecode = session["gamecode"]
    name = session['name']

    role = GAMES[gamecode].players[name]["role"]

    session["role"] = role

    join_room(gamecode + "/player")
    logging.debug(f"User {session['name']} has joined the socket room [{gamecode}/player]")

    if "role" in session:
        join_room(gamecode + "/" + role)
        logging.debug(f"User {session['name']} has joined the socket room [{gamecode}/{role}]")


@socketio.on("getPlayerData")
def getPlayerData():
    name = session["name"]
    gamecode = session["gamecode"]

    player = GAMES[gamecode].players[name]

    emit("playerData", player)

@socketio.on("alertRoom")
def alertRoom(data):
    message = data["message"]
    room = data["room"]

    gamecode = session["gamecode"]
    gameroom = gamecode + "/" + room

    logging.debug(f"Sending alertMessage to {gameroom} (message: {message})")
    emit("alertMessage", {"message": message}, to=gameroom)


# Helper command
def isAuthorised(player_role, round_status):
    return True

@socketio.on("sendMessage")
def sendMessage(data):
    gamecode = session["gamecode"]
    name = session["name"]

    game = GAMES[gamecode]
    player = GAMES[gamecode].players[name]

    role = player["role"]

    sender = player["alias"]
    message = data["message"]

    logging.debug(f"[GC: {gamecode}] Message received from {name}: {message}")

    if player["status"] != "online":
        message = "You are offline. Better luck next time."
        emit("message", {"sender": sender, "message": message})
        return

    if not isAuthorised(role, game.roundStatus):
        message = "You cannot chat at this point in time."
        emit("message", {"sender": sender, "message": message})
        return

    else:
        if game.roundStatus < 3:
            sender = "Anonymous"
            gameroom = gamecode + "/" + role

        else:
            gameroom = gamecode + "/player"

        logging.debug(f"[GC: {gamecode}] Sending message to {gameroom}")
        emit("message", {"sender": sender, "message": message}, to=gameroom)


if __name__ == "__main__":
    socketio.run(app=app, host="0.0.0.0", port="5000")